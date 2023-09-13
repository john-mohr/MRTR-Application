from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

def validate_date(value):
    if value > timezone.localtime(timezone=timezone.get_current_timezone()).date():
        raise ValidationError('Ensure this value is not a future date')


def validate_phone(value):
    if value != '' and len(value) != 10:
        raise ValidationError('Ensure this value is a valid phone number')


class Resident(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10, blank=True, validators=[validate_phone])
    email = models.EmailField(max_length=62, blank=True)
    admit_date = models.DateField(default=timezone.now)
    rent = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(1000)])
    bed = models.OneToOneField('Bed', on_delete=models.CASCADE, blank=True, null=True)
    door_code = models.CharField(max_length=4, blank=True)
    referral_info = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    discharge_date = models.DateField(blank=True, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/resident/%i' % self.id

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def balance(self):
        return Transaction.objects.filter(resident=self.id).aggregate(models.Sum('amount'))['amount__sum']

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Transaction(models.Model):
    date = models.DateField(default=timezone.now, validators=[validate_date])
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    # TODO (wait) Cut down on the amount of transaction types
    TYPE_CHOICES = [
        # Auto apply
        ('Rent charge', 'Rent charge'),                 # 0
        ('Refund', 'Refund'),                           # 1
        ('Incentive', 'Incentive'),                     # 2
        ('Rent adjustment', 'Rent adjustment'),         # 3

        # Decrease balance
        ('Rent payment', 'Rent payment'),               # 4
        ('Bonus', 'Bonus'),                             # 5
        # ('Work/reimbursement', 'Work/reimbursement'),   # 6
        # ('Sober support', "Sober support"),             # 7

        # Increase balance
        ('Fee', 'Fee'),                                 # 8
        # ('Loan', 'Loan'),                               # 9

        # Other
        ('Fix', 'Fix'),                                 # 10
        ('Other (specify)', 'Other (specify)')          # 11
    ]
    type = models.CharField(max_length=30, blank=True)
    METHOD_CHOICES = [
        # ('', ''),
        ('ACH', 'ACH'),
        ('Cash', 'Cash'),
        ('Cash App', 'Cash App'),
        ('Check', 'Check'),
        ('Money Order', 'Money Order'),
        ('PayPal', 'PayPal'),
        ('Venmo', 'Venmo'),
        ('Zelle', 'Zelle'),
        ('Other (specify)', 'Other (specify)')
    ]
    method = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_trans/%i' % self.id


class House(models.Model):
    name = models.CharField(max_length=25)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=2)
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/house/' + self.name

    def __str__(self):
        return self.name


class Bed(models.Model):
    name = models.CharField(max_length=7)
    house = models.ForeignKey('House', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Drug_test(models.Model):
    date = models.DateField(default=timezone.now, validators=[validate_date], blank=True, null=True)
    RESULT_CHOICES = [
        ('Negative', 'Negative'),
        ('Positive', 'Positive'),
        ('Positive (Meds)', 'Positive (Meds)'),
        ('Invalid', 'Invalid'),
        ('Other (Specify)', 'Other (Specify)')
    ]
    result = models.CharField(max_length=17, choices=RESULT_CHOICES)
    substances = models.TextField(blank=True)
    notes = models.CharField(max_length=50, blank=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE,
                                db_column='manager_id', related_name='dt_manager', blank=True, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True,  null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_dtest/%i' % self.id


class Check_in(models.Model):
    date = models.DateField(default=timezone.localtime(timezone.now()), validators=[validate_date])
    METHOD_CHOICES = [
        ('In person', 'In person'),
        ('Phone call', 'Phone call'),
        ('Text', 'Text')
    ]
    method = models.CharField(max_length=12, choices=METHOD_CHOICES)
    notes = models.TextField(blank=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE,
                                db_column='manager_id', related_name='ci_manager', blank=True, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_check_in/%i' % self.id


class Site_visit(models.Model):
    date = models.DateField(default=timezone.now, validators=[validate_date])
    issues = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_site_visit/%i' % self.id


class House_meeting(models.Model):
    date = models.DateField(default=timezone.now, validators=[validate_date])
    issues = models.TextField(blank=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_house_meeting/%i' % self.id


class Absentee(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)  # automatic
    meeting = models.ForeignKey('House_meeting', on_delete=models.CASCADE)  # automatic


class Shopping_trip(models.Model):
    date = models.DateField(default=timezone.now, validators=[validate_date])
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/shopping_trip/%i' % self.id


class Supply_request(models.Model):
    PRODUCT_CHOICES = [
        ('Paper towels', 'Paper towels'),
        ('Toilet paper', 'Toilet paper'),
        ('Laundry detergent', 'Laundry detergent'),
        ('Disinfectant wipes', 'Disinfectant wipes'),
        ('Garbage bags - kitchen', 'Garbage bags - kitchen'),
        ('Garbage bags - yard', 'Garbage bags - yard'),
        ('Dish soap', 'Dish soap'),
        ('Dishwashing detergent', 'Dishwashing detergent'),
        ('Dish sponges', 'Dish sponges'),
        ('Glass cleaner', 'Glass cleaner'),
        ('All-purpose cleaner', 'All-purpose cleaner'),
        ('Spray bottle', 'Spray bottle'),
        ('Swiffer pads', 'Swiffer pads'),
        ('Sheet set - twin', 'Sheet set - twin'),
        ('Sheet set - full', 'Sheet set - full'),
        ('Comforter - twin', 'Comforter - twin'),
        ('Comforter - full', 'Comforter - full'),
        ('Pillow', 'Pillow'),
        ('Sign-out logs', 'Sign-out logs'),
        ('Visitor logs', 'Visitor logs'),
        ('Itinerary sheets', 'Itinerary sheets'),
        ('Leave request forms', 'Leave request forms'),
        ('B mod forms', 'B mod forms'),
        ('Emergency contact forms', 'Emergency contact forms'),
        ('UA kits', 'UA kits'),
        ('Other', 'Other')
    ]
    products = models.TextField(blank=True)
    other = models.CharField(max_length=50, blank=True)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    fulfilled = models.BooleanField(default=False)  # automatic
    trip = models.ForeignKey('Shopping_trip', on_delete=models.CASCADE, blank=True, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_supply_request/%i' % self.id


class Maintenance_request(models.Model):
    issue = models.TextField()
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    fulfilled = models.BooleanField(default=False)  # automatic
    fulfillment_date = models.DateField(null=True)
    fulfillment_notes = models.TextField(blank=True)
    fulfillment_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(blank=True, null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_maintenance_request/%i' % self.id


# TODO (wait) ask TC if the app needs a section for manager meetings
# class Manager_meeting(models.Model):
#     title = models.CharField(max_length=150)
#     issues = models.TextField(blank=True)
#     date = models.DateField(default=timezone.now)
#     location = models.CharField(max_length=50)
#     attendee = models.TextField(blank=True)
#     minutes_discussed = models.BooleanField()
#     submission_date = models.DateTimeField(default=timezone.now)  # automatic
#     last_update = models.DateTimeField(blank=True, null=True)  # automatic
#
#     def get_absolute_url(self):
#         return '/portal/meeting/%i' % self.id
