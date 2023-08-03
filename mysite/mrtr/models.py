from django.db import models
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.db.models import Sum
from django.db.models import CharField, Model

class Resident(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], null=True)
    email = models.EmailField(max_length=62, null=True)
    admit_date = models.DateField(default=timezone.now)
    rent = models.IntegerField(validators=[MaxValueValidator(1000)])
    bed = models.OneToOneField('Bed', on_delete=models.CASCADE, blank=True, null=True)
    door_code = models.IntegerField(validators=[MaxValueValidator(9999)], null=True)
    referral_info = models.TextField(null=True)
    notes = models.TextField(null=True)
    discharge_date = models.DateField(null=True)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/resident/%i' % self.id

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def balance(self):
        return Transaction.objects.filter(resident=self.id).aggregate(Sum('amount'))['amount__sum']

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Transaction(models.Model):
    date = models.DateField(default=timezone.now)
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
        ('Work/reimbursement', 'Work/reimbursement'),   # 6
        ('Sober support', "Sober support"),             # 7

        # Increase balance
        ('Fee', 'Fee'),                                 # 8
        ('Loan', 'Loan'),                               # 9

        # Other
        ('Fix', 'Fix'),                                 # 10
        ('Other (specify)', 'Other (specify)')          # 11
    ]
    type = models.CharField(max_length=30, blank=True)
    METHOD_CHOICES = [
        ('', ''),
        ('ACH', 'ACH'),
        ('Cash', 'Cash'),
        ('Cash App', 'Cash App'),
        ('Check', 'Check'),
        ('Money order', 'Money order'),
        ('PayPal', 'PayPal'),
        ('Venmo', 'Venmo'),
        ('Zelle', 'Zelle'),
        ('Other (specify)', 'Other (specify)')
    ]
    method = models.CharField(max_length=15, blank=True)
    notes = models.TextField(null=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_trans/%i' % self.id


class House(models.Model):
    name = models.CharField(max_length=25)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', null=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=2)
    last_update = models.DateTimeField(null=True)  # automatic

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
    date = models.DateField(default=timezone.now, blank=True)
    RESULT_CHOICES = [
        ('Negative', 'Negative'),
        ('Positive', 'Positive'),
        ('Positive (meds)', 'Positive (meds)'),
        ('Invalid', 'Invalid'),
        ('Other (specify)', 'Other (specify)')
    ]
    result = models.CharField(max_length=17, choices=RESULT_CHOICES)

    substances = models.TextField(null=True)

    # amphetamines = models.BooleanField()
    # barbiturates = models.BooleanField()
    # benzodiazepines = models.BooleanField()
    # cocaine = models.BooleanField()
    # marijuana = models.BooleanField()
    # opiates = models.BooleanField()
    # phencyclidine = models.BooleanField()

    notes = models.CharField(max_length=50, null=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_dtest/%i' % self.id


class Check_in(models.Model):
    date = models.DateField(default=timezone.now)
    METHOD_CHOICES = [
        ('In person', 'In person'),
        ('Phone call', 'Phone call'),
        ('Text', 'Text')
    ]
    method = models.CharField(max_length=12, choices=METHOD_CHOICES)
    notes = models.TextField(null=True)
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE,
                                db_column='manager_id', related_name='manager', blank=True, null=True)  # maybe add limit_to() argument
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_check_in/%i' % self.id


class Shopping_trip(models.Model):
    date = models.DateTimeField(default=timezone.now)  #blank=True, null=True)  # automatic
    amount = models.DecimalField(max_digits=6, decimal_places=2)  #, blank=True, null=True)
    notes = models.TextField(null=True)
    
    def get_absolute_url(self):
        return '/portal/shopping_trip/%i' % self.id


class Supply_request(models.Model):
    date = models.DateTimeField(default=timezone.now)  #blank=True, null=True)  # automatic
    PRODUCT_CHOICES = [
        ('ppt', 'Paper towels'),
        ('tpp', 'Toilet paper'),
        ('ldt', 'Laundry detergent'),
        ('diw', 'Disinfectant wipes'),
        ('kgb', 'Garbage bags - kitchen'),
        ('ygb', 'Garbage bags - yard'),
        ('dso', 'Dish soap'),
        ('dwd', 'Dishwashing detergent'),
        ('dsp', 'Dish sponges'),
        ('glc', 'Glass cleaner'),
        ('apc', 'All-purpose cleaner'),
        ('spb', 'Spray bottle'),
        ('swp', 'Swiffer pads'),
        ('sst', 'Sheet set - twin'),
        ('ssf', 'Sheet set - full'),
        ('cmt', 'Comforter - twin'),
        ('cmf', 'Comforter - full'),
        ('plw', 'Pillow'),
        ('sol', 'Sign-out logs'),
        ('vil', 'Visitor logs'),
        ('ilr', 'Itinerary/leave request forms'),
        ('bmd', 'B Mod Forms'),
        ('ech', 'Meds/emergency contact sheets'),
        ('uak', 'UA kits'),
        ('oth', 'Other (specify')
    ]
    product = models.CharField(max_length=3, choices=PRODUCT_CHOICES, null=True)
    other = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField(validators=[MaxValueValidator(10)])
    notes = models.TextField(null=True, blank=True)
    fulfilled = models.BooleanField()  # automatic
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    trip = models.ForeignKey('Shopping_trip', on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return '/portal/supply_request/%i' % self.id


class Site_visit(models.Model):
    date = models.DateField(default=timezone.now)
    issues = models.TextField(null=True)
    explanation = models.TextField(null=True)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_site_visit/%i' % self.id


class House_meeting(models.Model):
    date = models.DateField(default=timezone.now)
    issues = models.TextField(null=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    manager = models.ForeignKey('Resident', on_delete=models.CASCADE, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument
    submission_date = models.DateTimeField(default=timezone.now)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/edit_house_meeting/%i' % self.id


class Absentee(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE)
    meeting = models.ForeignKey('House_meeting', on_delete=models.CASCADE)  # automatic


# TODO (wait) ask TC if she's still doing manager meetings
class Manager_meeting(models.Model):
    title = models.CharField(max_length=150)
    issues = models.TextField(null=True)
    date = models.DateField(default=timezone.now)  #blank=True, null=True)
    location = models.CharField(max_length=50)
    attendee = models.TextField(null=True)
    minutes_discussed = models.BooleanField()
    submission_date = models.DateTimeField(default=timezone.now)  #blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic

    def get_absolute_url(self):
        return '/portal/meeting/%i' % self.id


# class Attendee(models.Model):
#     meeting = models.ForeignKey('Manager_meeting', on_delete=models.CASCADE)  #, blank=True, null=True)
#     manager = models.ForeignKey('Resident', on_delete=models.CASCADE)  #, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument


# class Manager_issue(models.Model):
#     description = models.CharField(max_length=200)
#     STATUS_CHOICES = [
#         ('n', 'New'),
#         ('o', 'Ongoing')
#     ]
#     status = models.CharField(max_length=1, choices=STATUS_CHOICES, null=True)
#     expected_completion = models.DateField()  #blank=True, null=True)
#     meeting = models.ForeignKey('Manager_meeting', on_delete=models.CASCADE)  #, blank=True, null=True)  # automatic
#     submission_date = models.DateTimeField(default=timezone.now)  #blank=True, null=True)  # automatic
#     last_update = models.DateTimeField(null=True)  # automatic


