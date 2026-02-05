from django.urls import path
from . import views

urlpatterns = [
    # ---------------------------------------
    # Auth
    # ---------------------------------------
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ---------------------------------------
    # Dashboard
    # ---------------------------------------
    path('dashboard/', views.dashboard, name='dashboard'),

    # ---------------------------------------
    # Service CRUD
    # ---------------------------------------
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/update/<int:pk>/', views.update_service, name='update_service'),
    path('services/delete/<int:pk>/', views.delete_service, name='delete_service'),

    # ---------------------------------------
    # Appointments
    # ---------------------------------------
    path('appointments/book/', views.book_appointment, name='book_appointment'),

    # ---------------------------------------
    # Feedback
    # ---------------------------------------
    path('feedback/<int:appointment_id>/', views.give_feedback, name='give_feedback'),

    # ---------------------------------------
    # Exercise
    # ---------------------------------------
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/create/', views.exercise_create, name='exercise_create'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:exercise_id>/update/', views.exercise_update, name='exercise_update'),
    path('exercises/<int:exercise_id>/delete/', views.exercise_delete, name='exercise_delete'),


    # ---------------------------------------
    # Treatment Plans
    # ---------------------------------------
    path('treatment_plan_list', views.treatment_plan_list, name='treatment_plan_list'),
    path('create/', views.treatment_plan_create, name='treatment_plan_create'),
    path('create-for-appointment/<int:appointment_id>/', views.treatment_plan_create_for_appointment, name='treatment_plan_create_for_appointment'),
    path('<int:pk>/', views.treatment_plan_detail, name='treatment_plan_detail'),
    path('<int:pk>/update/', views.treatment_plan_update, name='treatment_plan_update'),
    path('<int:pk>/delete/', views.treatment_plan_delete, name='treatment_plan_delete'),

    # ---------------------------------------
    # Notifications
    # ---------------------------------------
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/update/<int:pk>/', views.notification_update, name='notification_update'),
    path('notifications/delete/<int:pk>/', views.notification_delete, name='notification_delete'),

    # ---------------------------------------
    # Availability Slots
    # ---------------------------------------
    path('availability/', views.availability_slot_list, name='availability_slot_list'),
    path('availability/add/', views.availability_slot_create, name='availability_slot_create'),
    path('availability/<int:pk>/edit/', views.availability_slot_update, name='availability_slot_update'),
    path('availability/<int:pk>/delete/', views.availability_slot_delete, name='availability_slot_delete'),

    # ---------------------------------------
    # Location Coverage
    # ---------------------------------------
    path('coverage/', views.coverage_list, name='coverage_list'),
    path('coverage/add/', views.coverage_create, name='coverage_create'),
    path('coverage/<int:pk>/edit/', views.coverage_update, name='coverage_update'),
    path('coverage/<int:pk>/delete/', views.coverage_delete, name='coverage_delete'),

    # ---------------------------------------
    # Payments
    # ---------------------------------------
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/success/', views.payment_success, name='payment_success'),

    # ---------------------------------------
    # Discount Coupons
    # ---------------------------------------
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/add/', views.coupon_create, name='coupon_create'),
    path('coupons/<int:pk>/edit/', views.coupon_update, name='coupon_update'),
    path('coupons/<int:pk>/delete/', views.coupon_delete, name='coupon_delete'),
    path('coupons/<int:pk>/apply/', views.coupon_apply, name='coupon_apply'),

    # ---------------------------------------
    # Emergency Requests
    # ---------------------------------------
    path('emergency/', views.emergency_list, name='emergency_list'),
    path('emergency/create/', views.emergency_create, name='emergency_create'),
    path('emergency/<int:pk>/update/', views.emergency_update, name='emergency_update'),
    path('emergency/<int:pk>/delete/', views.emergency_delete, name='emergency_delete'),

    # ---------------------------------------
    # Chat Messages
    # ---------------------------------------
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/send/', views.chat_create, name='chat_create'),
    path('chat/<int:pk>/delete/', views.chat_delete, name='chat_delete'),

    # ---------------------------------------
    # Support Tickets
    # ---------------------------------------
    path('support/', views.ticket_list, name='ticket_list'),
    path('support/create/', views.ticket_create, name='ticket_create'),
    path('support/<int:pk>/update/', views.ticket_update, name='ticket_update'),
    path('support/<int:pk>/delete/', views.ticket_delete, name='ticket_delete'),

    # ---------------------------------------
    # Therapist Leaves
    # ---------------------------------------
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/request/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/update/', views.leave_update, name='leave_update'),
    path('leaves/<int:pk>/delete/', views.leave_delete, name='leave_delete'),

    # ---------------------------------------
    # Home Exercise Reminders
    # ---------------------------------------
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('reminders/create/', views.reminder_create, name='reminder_create'),
    path('reminders/<int:pk>/update/', views.reminder_update, name='reminder_update'),
    path('reminders/<int:pk>/delete/', views.reminder_delete, name='reminder_delete'),

    # ---------------------------------------
    # Blog Articles
    # ---------------------------------------
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<int:pk>/edit/', views.blog_update, name='blog_update'),
    path('blog/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    # Add blog detail view if needed
    # path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # ---------------------------------------
    # FAQs
    # ---------------------------------------
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/create/', views.faq_create, name='faq_create'),
    path('faqs/<int:pk>/edit/', views.faq_update, name='faq_update'),
    path('faqs/<int:pk>/delete/', views.faq_delete, name='faq_delete'),

    # ---------------------------------------
    # Clinic Branches
    # ---------------------------------------
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/add/', views.branch_create, name='branch_create'),
    path('branches/<int:pk>/edit/', views.branch_update, name='branch_update'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),

    # ---------------------------------------
    # Subscription Plans
    # ---------------------------------------
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/create/', views.subscription_create, name='subscription_create'),
    path('subscriptions/<int:pk>/edit/', views.subscription_update, name='subscription_update'),
    path('subscriptions/<int:pk>/delete/', views.subscription_delete, name='subscription_delete'),

    # ---------------------------------------
    # Transactions
    # ---------------------------------------
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # ---------------------------------------
    # Analytics Reports
    # ---------------------------------------
    path('analytics/', views.analytics_list, name='analytics_list'),
    path('analytics/create/', views.analytics_create, name='analytics_create'),
    path('analytics/<int:pk>/edit/', views.analytics_update, name='analytics_update'),
    path('analytics/<int:pk>/delete/', views.analytics_delete, name='analytics_delete'),

    # ---------------------------------------
    # Recovery Predictions
    # ---------------------------------------
    path('recovery-predictions/', views.recovery_list, name='recovery_list'),
    path('recovery-predictions/create/', views.recovery_create, name='recovery_create'),
    path('recovery-predictions/<int:pk>/edit/', views.recovery_update, name='recovery_update'),
    path('recovery-predictions/<int:pk>/delete/', views.recovery_delete, name='recovery_delete'),
]