from django.db import models
from django.core.validators import MaxValueValidator


class Resident(models.Model):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    phone = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], null=True)
    email = models.EmailField(max_length=62, null=True)
    admit_date = models.DateField(blank=True, null=True)
    rent = models.IntegerField(validators=[MaxValueValidator(1000)], blank=True, null=True)
    door_code = models.IntegerField(validators=[MaxValueValidator(9999)], null=True)
    bed = models.OneToOneField('Bed', on_delete=models.PROTECT, blank=True, null=True)
    referral_info = models.TextField(null=True)
    notes = models.TextField(null=True)
    discharge_date = models.DateField(null=True)
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Transaction(models.Model):
    date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    TYPE_CHOICES = [
        # Auto apply
        ('rnt', 'Rent charge'),
        ('rfd', 'Refund'),
        ('inc', 'Sober incentive'),
        ('nra', 'New rent amount adjustment'),

        # Increase balance
        ('fee', 'Assess fee'),
        ('lon', 'Loan (will pay back)'),

        # Decrease balance
        ('pmt', 'Rent payment'),
        ('bon', 'Bonus'),
        ('wrk', 'Work/reimbursement'),
        ('sos', "Sober support (won't pay back)"),

        # Other
        ('fix', 'Balance fix'),
        ('oth', 'Other adjustment (specify)')
    ]
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    METHOD_CHOICES = [
        ('ach', 'ACH'),
        ('csh', 'Cash'),
        ('cap', 'Cash App'),
        ('chk', 'Check'),
        ('mod', 'Money order'),
        ('ppl', 'PayPal'),
        ('vnm', 'Venmo'),
        ('zel', 'Zelle'),
        ('oth', 'Other (specify)')
    ]
    method = models.CharField(max_length=3, choices=METHOD_CHOICES, null=True)
    notes = models.TextField(null=True)
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, blank=True, null=True)
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Drug_test(models.Model):
    date = models.DateField(blank=True, null=True)
    RESULT_CHOICES = [
        ('neg', 'Negative'),
        ('pos', 'Positive'),
        ('med', 'Positive (meds)'),
        ('inv', 'Invalid'),
        ('oth', 'Other (specify)')
    ]
    result = models.CharField(max_length=3, choices=RESULT_CHOICES)
    amphetamines = models.BooleanField(blank=True, null=True)
    barbiturates = models.BooleanField(blank=True, null=True)
    benzodiazepines = models.BooleanField(blank=True, null=True)
    cocaine = models.BooleanField(blank=True, null=True)
    marijuana = models.BooleanField(blank=True, null=True)
    opiates = models.BooleanField(blank=True, null=True)
    phencyclidine = models.BooleanField(blank=True, null=True)
    other = models.CharField(max_length=50, null=True)
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, blank=True, null=True)
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Rent_change(models.Model):
    date = models.DateField(blank=True, null=True)
    old = models.IntegerField(validators=[MaxValueValidator(1000)], blank=True, null=True)
    new = models.IntegerField(validators=[MaxValueValidator(1000)], blank=True, null=True)
    notes = models.TextField(null=True)
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, blank=True, null=True)
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class House(models.Model):
    name = models.CharField(max_length=25)
    manager = models.ForeignKey('Resident', on_delete=models.PROTECT, db_column='manager_id', null=True)


class Bed(models.Model):
    name = models.CharField(max_length=7, blank=True, null=True)
    house = models.ForeignKey('House', on_delete=models.PROTECT)


class Shopping_trip(models.Model):
    date = models.DateTimeField( blank=True, null=True)  # automatic
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    notes = models.TextField(null=True)


class Supply_request(models.Model):
    date = models.DateTimeField(blank=True, null=True)  # automatic
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
    other = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(validators=[MaxValueValidator(10)], blank=True, null=True)
    notes = models.TextField(null=True)
    fulfilled = models.BooleanField(blank=True, null=True)  # automatic
    house = models.ForeignKey('House', on_delete=models.PROTECT, blank=True, null=True)
    trip = models.ForeignKey('Shopping_trip', on_delete=models.PROTECT, blank=True, null=True)  # might be unnecessary


class Manager_meeting(models.Model):
    date = models.DateField( blank=True, null=True)
    location = models.CharField(max_length=50)
    minutes_discussed = models.BooleanField()
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Attendee(models.Model):
    meeting = models.ForeignKey('Manager_meeting', on_delete=models.PROTECT, blank=True, null=True)
    manager = models.ForeignKey('Resident', on_delete=models.PROTECT, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument


class Site_visit(models.Model):
    date = models.DateField(blank=True, null=True)
    issues = models.TextField(null=True)
    manager = models.ForeignKey('Resident', on_delete=models.PROTECT, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument
    house = models.ForeignKey('House', on_delete=models.PROTECT, blank=True, null=True)
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Manager_issue(models.Model):
    description = models.CharField(max_length=200)
    STATUS_CHOICES = [
        ('n', 'New'),
        ('o', 'Ongoing')
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, null=True)
    expected_completion = models.DateField(blank=True, null=True)
    meeting = models.ForeignKey('Manager_meeting', on_delete=models.PROTECT, blank=True, null=True)  # automatic
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Check_in(models.Model):
    date = models.DateField(blank=True, null=True)
    METHOD_CHOICES = [
        ('ip', 'In person'),
        ('pc', 'Phone call'),
        ('tx', 'Text')
    ]
    method = models.CharField(max_length=2, choices=METHOD_CHOICES)
    notes = models.TextField(null=True)
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, blank=True, null=True)
    manager = models.ForeignKey('Resident', on_delete=models.PROTECT, db_column='manager_id', related_name='manager', blank=True, null=True)  # maybe add limit_to() argument
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class House_meeting(models.Model):
    date = models.DateField( blank=True, null=True)
    issues = models.TextField(null=True),
    house = models.ForeignKey('House', on_delete=models.PROTECT, blank=True, null=True)
    manager = models.ForeignKey('Resident', on_delete=models.PROTECT, db_column='manager_id', blank=True, null=True)  # maybe add limit_to() argument
    submission_date = models.DateTimeField(blank=True, null=True)  # automatic
    last_update = models.DateTimeField(null=True)  # automatic


class Absentee(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, blank=True, null=True)
    meeting = models.ForeignKey('House_meeting', on_delete=models.PROTECT, blank=True, null=True)  # automatic