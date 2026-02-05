from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from django.contrib.auth.models import User  # ✅ Correct User import
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save

# -------------------------
# USER MODEL
# -------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Patient', 'Patient'),
        ('Therapist', 'Therapist'),
        ('Admin', 'Admin'),
        ('SupportStaff', 'Support Staff'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    specialization = models.CharField(max_length=255, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    availability_status = models.BooleanField(default=True)
    ratings_average = models.FloatField(default=0,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)
    verification_status = models.BooleanField(default=False)

    # ✅ Fix reverse accessor conflict
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        ordering = ['username']


# -------------------------
# THERAPIST PROFILE
# -------------------------
class TherapistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    bio = models.TextField(blank=True, null=True)
    expertise_areas = models.JSONField(default=dict)
    certifications = models.TextField(blank=True, null=True)
    visiting_radius_km = models.FloatField(default=10)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    total_patients_treated = models.PositiveIntegerField(default=0)
    daily_schedule = models.JSONField(default=dict)

    def __str__(self):
        return f"TherapistProfile of {self.user.username}"


# -------------------------
# PATIENT PROFILE
# -------------------------
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    medical_history = models.JSONField(default=dict)
    ongoing_conditions = models.TextField(blank=True, null=True)
    preferred_time_slots = models.JSONField(default=dict)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    last_session_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"PatientProfile of {self.user.username}"


# -------------------------
# SERVICE
# -------------------------
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    base_fee = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    # ✅ Changed: JSONField → TextField
    required_equipment = models.TextField(
        blank=True,
        help_text="List equipment, separated by commas"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# -------------------------
# APPOINTMENT
# -------------------------
class Appointment(models.Model):
    BOOKING_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Rescheduled', 'Rescheduled'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapist_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='Pending')
    payment_status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_fee(self):
        return self.service.base_fee

    def __str__(self):
        return f"{self.patient.username} → {self.therapist.username} ({self.scheduled_date})"


# -------------------------
# EXERCISE & TREATMENT PLAN
# -------------------------
class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    demo_video_url = models.URLField(blank=True, null=True)
    repetition_count = models.PositiveIntegerField(default=0)
    difficulty_level = models.CharField(max_length=50, blank=True, null=True)
    focus_area = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name



class TreatmentPlan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    appointment = models.ForeignKey(
        'Appointment', 
        on_delete=models.CASCADE,
        related_name='treatment_plans'
    )
    exercises_list = models.TextField(
        help_text="List of prescribed exercises (one exercise per line)"
    )
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescribed_treatment_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    follow_up_required = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    instructions = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Treatment Plan"
        verbose_name_plural = "Treatment Plans"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Treatment Plan for {self.appointment} - {self.created_at.date()}"
    
    def get_exercises_list(self):
        """Return exercises as a clean list"""
        if not self.exercises_list:
            return []
        
        exercises = []
        for line in self.exercises_list.strip().split('\n'):
            exercise = line.strip()
            if exercise:
                exercises.append(exercise)
        return exercises
    
    def set_exercises_list(self, exercises):
        """Set exercises from a list"""
        self.exercises_list = '\n'.join([ex.strip() for ex in exercises if ex.strip()])

class ProgressTracking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    
    completion_percentage = models.FloatField(default=0)
    feedback_notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)


# -------------------------
# FEEDBACK
# -------------------------
class Feedback(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_given')
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_received')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# -------------------------
# SIGNALS
# -------------------------
@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Therapist':
            TherapistProfile.objects.create(user=instance)
        elif instance.role == 'Patient':
            PatientProfile.objects.create(user=instance)


@receiver(post_save, sender=Feedback)
def update_therapist_rating(sender, instance, **kwargs):
    therapist = instance.therapist
    feedbacks = Feedback.objects.filter(therapist=therapist)
    avg_rating = feedbacks.aggregate(models.Avg('rating'))['rating__avg'] or 0
    therapist.ratings_average = avg_rating
    therapist.save()


# ------------------------- -------------------------
# Notification
# -------------------------
class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('Reminder', 'Reminder'),
        ('Update', 'Update'),
        ('Promotion', 'Promotion'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # ✅ Latest notification first

    def __str__(self):
        return f"{self.title} - {self.category}"

# -------------------------
# AvailabilitySlot
# -------------------------

class AvailabilitySlot(models.Model):
    therapist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']  # ✅ Show slots in chronological order
        unique_together = ('therapist', 'date', 'start_time', 'end_time')  # ✅ Prevent duplicate slots

    def __str__(self):
        return f"{self.therapist.username} | {self.date} | {self.start_time}-{self.end_time}"

# -------------------------
# LocationCoverage
# -------------------------


class LocationCoverage(models.Model):
    therapist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coverage_areas'
    )
    service_area_name = models.CharField(max_length=100)

    # Instead of PolygonField (requires GDAL), use TextField to store coordinates/area details
    location = models.TextField(
        help_text="Describe location or store coordinates (Lat/Lng)."
    )

    def __str__(self):
        return f"{self.service_area_name} - {self.therapist.username}"

# -------------------------
# Payment
# -------------------------


class Payment(models.Model):
    MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Wallet', 'Wallet'),
        ('Online', 'Online'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    # ✅ No need for direct import — avoid circular import error
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment.id}"



# -------------------------
# DiscountCoupon
# -------------------------


class DiscountCoupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    
    # ✅ Ensures discount is between 1–100%
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    valid_from = models.DateField()
    valid_to = models.DateField()

    # ✅ Prevents negative values
    min_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # ✅ Number of times this coupon can be used by a single user or overall
    max_usage = models.PositiveIntegerField(default=1)
    
    # ✅ Active / Deactivated coupon visibility
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% OFF"

    def is_valid(self):
        """Check if coupon is active and within date range"""
        from datetime import date
        today = date.today()
        return self.is_active and self.valid_from <= today <= self.valid_to


# -------------------------
# EmergencyRequest
# -------------------------


class EmergencyRequest(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('InProgress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_requests'
    )

    condition_description = models.TextField()

    requested_at = models.DateTimeField(auto_now_add=True)

    assigned_therapist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emergency_cases'
    )

    response_time = models.DurationField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Open'
    )

    def __str__(self):
        return f"Emergency - {self.patient.username} ({self.status})"



    def clean(self):
        # Ensure therapist is assigned when case is not open
        if self.status != 'Open' and not self.assigned_therapist:
            raise ValidationError("A therapist must be assigned before updating status.")

# -------------------------
# ChatMessage
# -------------------------


class ChatMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    message_text = models.TextField()

    attachment = models.FileField(
        upload_to='chat_attachments/',
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

# -------------------------
# SupportTicket
# -------------------------


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('InProgress', 'In Progress'),
        ('Closed', 'Closed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets'  # ✅ Helpful reverse lookup
    )
    
    issue_category = models.CharField(max_length=100)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Open'
    )

    response_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.user.username} ({self.status})"

# -------------------------
# TherapistLeave
# -------------------------

class TherapistLeave(models.Model):
    therapist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.therapist.username} Leave ({status}) {self.from_date} - {self.to_date}"

    def clean(self):
        # ✅ Validates date range
        if self.from_date > self.to_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("From date cannot be later than To date.")

# -------------------------
# HomeExerciseReminder
# -------------------------

class HomeExerciseReminder(models.Model):
    SENT_VIA = [
        ('SMS', 'SMS'),
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exercise_reminders"
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="exercise_reminders"
    )

    reminder_time = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    sent_via = models.CharField(
        max_length=20,
        choices=SENT_VIA,
        default='WhatsApp'  # ✅ Default option added
    )

    def __str__(self):
        return f"{self.patient.username} - {self.exercise.name} Reminder"

    class Meta:
        ordering = ['-reminder_time']  # ✅ Latest reminders at top

# -------------------------
# BlogArticle
# -------------------------

class BlogArticle(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_articles"
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated from title"
    )  # ✅ SEO-friendly URL support

    content = models.TextField()
    category = models.CharField(max_length=100)

    cover_image = models.ImageField(
        upload_to='blogs/',
        blank=True,
        null=True
    )

    tags = models.CharField(max_length=50, unique=True)

    published_at = models.DateTimeField(blank=True, null=True)

    is_published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # ✅ Auto-generate slug only if missing
        if not self.slug:
            self.slug = slugify(self.title)

        # ✅ Set published time automatically
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        # ✅ Clear published_at if post is unpublished
        if not self.is_published:
            self.published_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    class Meta:
        ordering = ['-published_at', '-id']  # ✅ New blogs shown first


# -------------------------
# FAQ
# -------------------------

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        # ✅ Display the first 50 characters of the question in admin panel
        return f"FAQ: {self.question[:50]}..."

    class Meta:
        ordering = ['category', 'id']  # ✅ Group FAQs by category automatically

# -------------------------
# ClinicBranch
# -------------------------

class ClinicBranch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)  # ✅ Replaced GIS Field
    opening_hours = models.TextField(
    blank=True,
    help_text="Example: Mon-Fri: 9AM - 7PM | Sat: 10AM - 2PM | Sun: Closed"
)
    def __str__(self):
        return self.name


# -------------------------
# SubscriptionPlan
# -------------------------

class SubscriptionPlan(models.Model):
    plan_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=255, null=True, blank=True)  # ✅ Updated

    def __str__(self):
        return self.plan_name

# -------------------------
# Transaction
# -------------------------

class Transaction(models.Model):
    PAYMENT_MODES = [
        ('UPI', 'UPI'),
        ('Card', 'Credit/Debit Card'),
        ('NetBanking', 'Net Banking'),
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE, related_name='transactions')  # ✅ Refer by string

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODES)
    transaction_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id}"

# -------------------------
# AnalyticsReport
# -------------------------

class AnalyticsReport(models.Model):
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_reports')
    total_sessions = models.PositiveIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    patient_retention_rate = models.FloatField(default=0.0)
    popular_services = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.therapist.username} - {self.created_at.date()}"

# -------------------------
# RecoveryPredictor
# -------------------------

class RecoveryPredictor(models.Model):
    model_version = models.CharField(max_length=50)
    input_features = models.CharField(max_length=20)  # Stores ML model inputs (age, injury type, etc.)
    predicted_recovery_days = models.FloatField()  # ML predicted duration
    confidence_score = models.FloatField(default=0.0)  # Prediction confidence level

    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Track prediction time

    def __str__(self):
        return f"Recovery Model v{self.model_version} - {self.predicted_recovery_days} days"

# -------------------------
# SIGNALS
# -------------------------

@receiver(post_save, sender=Appointment)
def send_notification_on_appointment(sender, instance, created, **kwargs):
    if not instance.therapist:  # Safety check
        return

    title = "New Appointment Scheduled" if created else "Appointment Updated"

    Notification.objects.create(
        user=instance.therapist,
        title=title,
        message=f"Status: {instance.booking_status} | Patient: {instance.patient.username}",
        category='Appointment'
    )


# ✅ Auto-generate exercise progress tracking on new treatment plan
@receiver(post_save, sender=TreatmentPlan)
def auto_generate_progress(sender, instance, created, **kwargs):
    if created:
        try:
            # Ensure appointment exists and has patient
            if not instance.appointment or not hasattr(instance.appointment, 'patient'):
                return
            
            patient = instance.appointment.patient
            exercises_list = instance.get_exercises_list()
            
            if not exercises_list:
                return
            
            # Import here to avoid circular imports
            from .models import Exercise, ProgressTracking
            
            for exercise_name in exercises_list:
                if not exercise_name or not isinstance(exercise_name, str):
                    continue
                
                # Get or create exercise
                exercise_obj, _ = Exercise.objects.get_or_create(
                    name=exercise_name.strip(),
                    defaults={
                        'description': f'Auto-generated from TreatmentPlan #{instance.id}',
                        'difficulty_level': 'beginner'
                    }
                )
                
                # Create progress tracking if doesn't exist
                ProgressTracking.objects.get_or_create(
                    patient=patient,
                    exercise=exercise_obj,
                    treatment_plan=instance,
                    defaults={
                        'status': 'assigned',
                        'assigned_date': instance.created_at
                    }
                )
                
        except Exception as e:
            # Log the error but don't crash the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating progress tracking for TreatmentPlan {instance.id}: {str(e)}")

