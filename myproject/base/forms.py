from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Appointment, Service, Exercise, Feedback, TreatmentPlan, Notification, AvailabilitySlot, LocationCoverage, SubscriptionPlan, Transaction, Payment, DiscountCoupon, EmergencyRequest, ChatMessage, SupportTicket, TherapistLeave, HomeExerciseReminder, BlogArticle, FAQ, ClinicBranch, AnalyticsReport, RecoveryPredictor
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify





# -------------------------
# USER REGISTRATION FORM
# -------------------------
class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Patient', 'Patient'),
        ('Therapist', 'Therapist'),
        ('Admin', 'Admin'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    gender = forms.Select(attrs={'class': 'form-select'})
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'phone_number', 'gender', 'role', 'password1', 'password2', 'profile_picture'
        ]

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


# -------------------------
# LOGIN FORM
# -------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))


# -------------------------
# SERVICE FORM
# -------------------------
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'base_fee', 'image', 'required_equipment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'required_equipment': forms.Textarea(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'base_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# -------------------------
# APPOINTMENT BOOKING FORM
# -------------------------
class AppointmentForm(forms.ModelForm):
    scheduled_date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}
    ))
    scheduled_time = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time', 'class': 'form-control'}
    ))

    class Meta:
        model = Appointment
        fields = ['therapist', 'service', 'scheduled_date', 'scheduled_time']

        widgets = {
            'therapist': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }

    # ✅ Only show Therapists in dropdown
    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['therapist'].queryset = User.objects.filter(role="Therapist")


# -------------------------
# EXERCISE FORM
# -------------------------
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'demo_video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'repetition_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty_level': forms.TextInput(attrs={'class': 'form-control'}),
            'focus_area': forms.TextInput(attrs={'class': 'form-control'}),
        }


# -------------------------
# TREATMENT PLAN FORM
# -------------------------
class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = [
            'appointment',
            'exercises_list',
            'prescribed_by',
            'follow_up_required',
            'status',
            'instructions'
        ]
        widgets = {
            'appointment': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Appointment'
            }),
            'exercises_list': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter one exercise per line...',
                'rows': 5
            }),
            'prescribed_by': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Prescribing Therapist'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional instructions...',
                'rows': 3
            }),
        }
        help_texts = {
            'exercises_list': 'Enter each exercise on a separate line',
            'follow_up_required': 'Check if patient needs follow-up',
        }

    def clean_exercises_list(self):
        exercises_list = self.cleaned_data.get('exercises_list', '')
        
        if not exercises_list.strip():
            raise forms.ValidationError("At least one exercise is required.")
        
        exercises = [ex.strip() for ex in exercises_list.split('\n') if ex.strip()]
        if not exercises:
            raise forms.ValidationError("Please enter valid exercises.")
        
        return exercises_list


# -------------------------
# FEEDBACK FORM
# -------------------------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1, 'max': 5
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Write feedback...',
                'rows': 3
            }),
        }

# ------------------------- -------------------------
# NotificationForm
# -------------------------

class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = [
            'user',
            'title',
            'message',
            'category',
            'is_read',
        ]

        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title',
                'maxlength': '100',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message...',
                'rows': 4,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'is_read': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    # ✅ Optional: Custom validation
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title


# ---------------------------------------
# AvailabilitySlot Form
# ---------------------------------------
class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time', 'is_booked']

        widgets = {
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'min': timezone.now().date(),
                }
            ),
            'start_time': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time',
                }
            ),
            'end_time': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time',
                }
            ),
            'is_booked': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            )
        }

        labels = {
            'date': 'Available Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'is_booked': 'Slot Already Booked?',
        }

    # ✅ Validation: Prevent invalid time ranges
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and end and end <= start:
            self.add_error('end_time', 'End time must be greater than start time.')

        return cleaned_data


# ---------------------------------------
# LocationCoverage Form
# ---------------------------------------
class LocationCoverageForm(forms.ModelForm):
    class Meta:
        model = LocationCoverage
        fields = ['service_area_name', 'location']

        widgets = {
            'service_area_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g., Koramangala',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g., Bengalore',
                }
            ),
        }

        labels = {
            'service_area_name': 'Service Area Name',
            'location': 'Location / Coordinates',
        }


# ---------------------------------------
# Payment Form
# ---------------------------------------
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['appointment', 'amount', 'mode', 'payment_status', 'transaction_id']

        widgets = {
            'appointment': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'mode': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'payment_status': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'transaction_id': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter unique transaction ID'}
            ),
        }

        labels = {
            'appointment': 'Appointment',
            'amount': 'Amount (₹)',
            'mode': 'Payment Mode',
            'payment_status': 'Payment Status',
            'transaction_id': 'Transaction ID',
        }


# ---------------------------------------
# DiscountCoupon Form
# ---------------------------------------
class DiscountCouponForm(forms.ModelForm):
    class Meta:
        model = DiscountCoupon
        fields = [
            'code', 'description', 'discount_percentage', 
            'valid_from', 'valid_to', 'min_amount', 
            'max_usage', 'is_active'
        ]

        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coupon Code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_usage': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'code': 'Coupon Code',
            'description': 'Description',
            'discount_percentage': 'Discount (%)',
            'valid_from': 'Valid From',
            'valid_to': 'Valid To',
            'min_amount': 'Minimum Amount (₹)',
            'max_usage': 'Max Usage',
            'is_active': 'Active?',
        }

    # ✅ Custom validation to ensure valid_from <= valid_to
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')

        if valid_from and valid_to and valid_from > valid_to:
            self.add_error('valid_to', "Valid To date must be after Valid From date.")
        return cleaned_data


# ---------------------------------------
# EmergencyRequest Form
# ---------------------------------------
class EmergencyRequestForm(forms.ModelForm):
    class Meta:
        model = EmergencyRequest
        fields = ['patient', 'condition_description', 'assigned_therapist', 'status']

        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'condition_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the emergency condition'
            }),
            'assigned_therapist': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'patient': 'Patient',
            'condition_description': 'Condition Description',
            'assigned_therapist': 'Assigned Therapist',
            'status': 'Status',
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        therapist = cleaned_data.get('assigned_therapist')

        if status != 'Open' and not therapist:
            raise ValidationError("A therapist must be assigned before updating status.")
        return cleaned_data


# ---------------------------------------
# ChatMessage Form
# ---------------------------------------
class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['sender', 'receiver', 'message_text', 'attachment']

        widgets = {
            'sender': forms.Select(attrs={'class': 'form-select'}),
            'receiver': forms.Select(attrs={'class': 'form-select'}),
            'message_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...'
            }),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'sender': 'Sender',
            'receiver': 'Receiver',
            'message_text': 'Message',
            'attachment': 'Attachment (optional)',
        }


# ---------------------------------------
# SupportTicket Form
# ---------------------------------------
class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['user', 'issue_category', 'description', 'status', 'response_message']

        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'issue_category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issue category'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the issue'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'response_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Response (optional)'}),
        }

        labels = {
            'user': 'User',
            'issue_category': 'Category',
            'description': 'Description',
            'status': 'Status',
            'response_message': 'Response',
        }


# ---------------------------------------
# TherapistLeave Form
# ---------------------------------------
class TherapistLeaveForm(forms.ModelForm):
    class Meta:
        model = TherapistLeave
        fields = ['therapist', 'from_date', 'to_date', 'reason', 'approved_by', 'is_approved']

        widgets = {
            'therapist': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'therapist': 'Therapist',
            'from_date': 'From Date',
            'to_date': 'To Date',
            'reason': 'Reason',
            'approved_by': 'Approved By',
            'is_approved': 'Approved',
        }

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if from_date and to_date and from_date > to_date:
            raise ValidationError("From date cannot be later than To date.")
        return cleaned_data


# ---------------------------------------
# HomeExerciseReminder Form
# ---------------------------------------
class HomeExerciseReminderForm(forms.ModelForm):
    class Meta:
        model = HomeExerciseReminder
        fields = ['patient', 'exercise', 'reminder_time', 'is_completed', 'sent_via']

        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'exercise': forms.Select(attrs={'class': 'form-select'}),
            'reminder_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sent_via': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'patient': 'Patient',
            'exercise': 'Exercise',
            'reminder_time': 'Reminder Time',
            'is_completed': 'Completed',
            'sent_via': 'Sent Via',
        }

# ---------------------------------------
# BlogArticle Form
# ---------------------------------------
class BlogArticleForm(forms.ModelForm):
    class Meta:
        model = BlogArticle
        fields = ['author', 'title', 'slug', 'content', 'category', 'cover_image', 'tags', 'is_published']

        widgets = {
            'author': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated from title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your content here'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated tags'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'author': 'Author',
            'title': 'Title',
            'slug': 'Slug',
            'content': 'Content',
            'category': 'Category',
            'cover_image': 'Cover Image',
            'tags': 'Tags',
            'is_published': 'Published',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        if not slug and title:
            slug = slugify(title)
        return slug


# ---------------------------------------
# FAQ Form
# ---------------------------------------
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'is_active']

        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Provide answer'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'question': 'Question',
            'answer': 'Answer',
            'category': 'Category',
            'is_active': 'Active',
        }


# ---------------------------------------
# ClinicBranch Form
# ---------------------------------------
class ClinicBranchForm(forms.ModelForm):
    class Meta:
        model = ClinicBranch
        fields = ['name', 'address', 'contact_number', 'location', 'opening_hours']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Branch address'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/Area or coordinates'}),
            'opening_hours': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '"Mon-Fri": "9:00-18:00"'}),
        }

        labels = {
            'name': 'Branch Name',
            'address': 'Address',
            'contact_number': 'Contact Number',
            'location': 'Location',
            'opening_hours': 'Opening Hours',
        }



# ---------------------------------------
# SubscriptionPlan Form
# ---------------------------------------
class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['plan_name', 'price', 'duration_days', 'is_active', 'location']

        widgets = {
            'plan_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter plan name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional: Specify region or city'}),
        }

        labels = {
            'plan_name': 'Plan Name',
            'price': 'Price',
            'features': 'Features',
            'duration_days': 'Duration (Days)',
            'is_active': 'Active',
            'location': 'Location',
        }

    def clean_features(self):
        features = self.cleaned_data.get('features')
        if not isinstance(features, dict):
            raise forms.ValidationError("Features must be a valid JSON dictionary.")
        return features


# ---------------------------------------
# Transaction Form
# ---------------------------------------
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'plan', 'amount', 'payment_mode', 'transaction_id', 'expires_at']

        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique transaction ID'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

        labels = {
            'user': 'User',
            'plan': 'Subscription Plan',
            'amount': 'Amount',
            'payment_mode': 'Payment Mode',
            'transaction_id': 'Transaction ID',
            'expires_at': 'Expiry Date/Time',
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount

# -------------------------
# AnalyticsReportForm
# -------------------------
class AnalyticsReportForm(forms.ModelForm):
    class Meta:
        model = AnalyticsReport
        fields = [
            'therapist',
            'total_sessions',
            'avg_rating',
            'revenue_generated',
            'patient_retention_rate',
            'popular_services'
        ]

        widgets = {
            'therapist': forms.Select(attrs={'class': 'form-control'}),
            'total_sessions': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'avg_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1, 'min': 0, 'max': 5}),
            'revenue_generated': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01, 'min': 0}),
            'patient_retention_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01, 'min': 0, 'max': 100}),
            'popular_services': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter popular services'}),
        }

    def clean_avg_rating(self):
        avg_rating = self.cleaned_data.get('avg_rating')
        if avg_rating < 0 or avg_rating > 5:
            raise forms.ValidationError("Average rating must be between 0 and 5.")
        return avg_rating

    def clean_patient_retention_rate(self):
        rate = self.cleaned_data.get('patient_retention_rate')
        if rate < 0 or rate > 100:
            raise forms.ValidationError("Retention rate must be between 0 and 100.")
        return rate

# -------------------------
# RecoveryPredictorForm
# -------------------------
class RecoveryPredictorForm(forms.ModelForm):
    class Meta:
        model = RecoveryPredictor
        fields = [
            'model_version',
            'input_features',
            'predicted_recovery_days',
            'confidence_score'
        ]

        widgets = {
            'model_version': forms.TextInput(attrs={'class': 'form-control'}),
            'input_features': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter input features '}),
            'predicted_recovery_days': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1, 'min': 0}),
            'confidence_score': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01, 'min': 0, 'max': 1}),
        }

    def clean_confidence_score(self):
        score = self.cleaned_data.get('confidence_score')
        if score < 0.0 or score > 1.0:
            raise forms.ValidationError("Confidence score must be between 0.0 and 1.0.")
        return score