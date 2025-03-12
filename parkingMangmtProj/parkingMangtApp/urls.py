from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('registerpage/', views.registerpage, name='registerpage'),
    path('loginpage/', views.loginpage, name='loginpage'),
    path('register/', views.register, name='register'),
    path('branchpage/', views.branchpage, name='branchpage'),
    path('login/', views.user_login, name='user_login'),
    path('businesspage/', views.businesspage, name='businesspage'),
    path('business/create/', views.create_business, name='business-create'),
    path('branch/create/', views.create_branch, name='branch-create'),
    path('branch/tables/', views.branch_tables, name='branch-tables'),
    path('business/tables/', views.business_tables, name='business-tables'),
    path('businesses/delete/<int:business_id>/', views.delete_business, name='delete_business'),
    path('user/tables/', views.user_tables, name='user-tables'),
    path('branches/', views.branches_view, name='branches'),
    path('branch/<int:branch_id>/', views.branch_detail22, name='branch_detail22'),
    # path('branch/<int:branch_id>/', views.branch_detail_view, name='branch-detail'),
    path('branch/<int:branch_id>/table', views.branc_ticket_table_view, name='branc_ticket_table'),
    path('branch/<int:branch_id>/slotfrom', views.parking_slot_from_branch, name='parking_slot_from_branch'),
    path('branch/<int:branch_id>/rates', views.parking_rates_form, name='parking_rates_form'),
    path('branch/<int:branch_id>/Add_Clients', views.Client_display_From, name='Client_display_From'),
    path('branches/<int:branch_id>/add-parking-slot/', views.add_parking_slot, name='add_parking_slot'),
    path('branch/<int:branch_id>/parking-slots/', views.view_parking_slots, name='view_parking_slots'),
    path('branch/<int:branch_id>/register-client/', views.register_client, name='register_client'),
    path('client/<int:client_id>/activate/', views.activate_client, name='activate-client'),
    path('clients/branch/<int:branch_id>/', views.clients_by_branch, name='clients_by_branch'),
    path('branch/<int:branch_id>/generate-ticket/', views.generate_ticket, name='generate_ticket'),
    path('ticket/<int:ticket_id>/download/', views.download_ticket, name='download_ticket'),
    path('add-rate/<int:branch_id>/', views.add_parking_rate, name='add_parking_rate'),
    path('ticket/clear/<int:ticket_id>/', views.clear_ticket, name='clear_ticket'),
    path('client/tables/', views.clients_table, name='clients_table'),
    path('delete-client/<int:client_id>/', views.delete_client, name='delete-client'),
    path('clients/branch/<int:branch_id>/',views.clients_table, name='clients_by_branch'),
    path('branchepermanager/', views.branch_list, name='branch_listpermanager'),
    path('delete-branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),


 
    path('branch/<int:branch_id>/expenditures/', views.branch_expenditures, name='branch_expenditures'),
    path('branch/<int:branch_id>/recent_expenses/', views.branch_recent_expenses, name='branch_recent_expenses'),
    path('branch/<int:branch_id>/add-expenditures/', views.add_expenditures, name='add_expenditures'),
    path('branch/expenditure/<int:expenditure_id>/edit/', views.edit_expenditure, name='edit_expenditure'),
    path('branch/expenditure/<int:expenditure_id>/delete/', views.delete_expenditure, name='delete_expenditure'),
    path('branch/add-category/', views.add_category_ajax, name='add_category_ajax'),
     path('branch/<int:branch_id>/update_balances/', views.update_balances, name='update_balances'),
     path('branch/<int:branch_id>/activity-report/', views.branch_activity_report, name='branch_activity_report'),
     path("branch/<int:branch_id>/export-csv/",views.export_branch_csv, name="export_branch_csv"),
    path("branch/<int:branch_id>/export-pdf/", views.export_branch_pdf, name="export_branch_pdf"),
 path('branch/<int:branch_id>/add_category/', views.add_category, name='add_category'),
   path('ticket/<int:ticket_id>/branch/<int:branch_id>/clear/', views.clear_ticket, name='clear_ticket'),
    path('clear_tickets', views.clear_tickets, name='clear_tickets'),
    path('ticket/<int:ticket_id>/branch/<int:branch_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),

    path('add-to-cart/<int:branch_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/<int:branch_id>/', views.checkout_cart, name='checkout_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),



     path('user-permissions/', views.user_permission, name='user_permission'),
]