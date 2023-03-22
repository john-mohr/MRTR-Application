from django.db import models
from django.core.validators import MaxValueValidator


class Resident(models.Model):
    first_name = models.CharField(max_length=50),
    last_name = models.CharField(max_length=50),
    phone = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True),
    email = models.EmailField(max_length=62, null=True),
    admit_date = models.DateField(),
    discharge_date = models.DateField(null=True),
    door_code = models.IntegerField(validators=[MaxValueValidator(9999)], null=True),
    rent = models.IntegerField(validators=[MaxValueValidator(1000)]),
    # balance = models.DecimalField(max_digits=8, decimal_places=2),
    referral_info = models.TextField(null=True),
    notes = models.TextField(null=True),
    house = models.ForeignKey('House', on_delete=models.PROTECT)
    # bed = models.ForeignKey('Bed', on_delete=models.PROTECT)


class Transaction(models.Model):
    date = models.DateField(),
    amount = models.DecimalField(max_digits=8, decimal_places=2),
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
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT)


class Drug_test(models.Model):
    date = models.DateField(),
    RESULT_CHOICES = [
        ('neg', 'Negative'),
        ('pos', 'Positive'),
        ('med', 'Positive (meds)'),
        ('inv', 'Invalid'),
        ('oth', 'Other (specify)')
    ]
    result = models.CharField(max_length=3, choices=RESULT_CHOICES)
    amphetamines = models.BooleanField(),
    barbiturates = models.BooleanField(),
    benzodiazepines = models.BooleanField(),
    cocaine = models.BooleanField(),
    marijuana = models.BooleanField(),
    opiates = models.BooleanField(),
    phencyclidine = models.BooleanField(),
    other = models.CharField(max_length=50, null=True),
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT),


class Rent_change(models.Model):
    date = models.DateField(),
    old = models.IntegerField(validators=[MaxValueValidator(1000)]),
    new = models.IntegerField(validators=[MaxValueValidator(1000)]),
    notes = models.TextField(null=True),
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT),


class House(models.Model):
    name = models.CharField(max_length=25)


class Bed(models.Model):
    name = models.CharField(max_length=5),
    house = models.ForeignKey('House', on_delete=models.PROTECT)
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT, null=True)


class Shopping_trip(models.Model):
    date = models.DateTimeField(),  # automatic
    amount = models.DecimalField(max_digits=6, decimal_places=2),
    notes = models.TextField(null=True)


class Supply_request(models.Model):
    date = models.DateTimeField(),  # automatic
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
    quantity = models.IntegerField(validators=[MaxValueValidator(10)]),
    notes = models.TextField(null=True)
    fulfilled = models.BooleanField(),  # automatic
    house = models.ForeignKey('House', on_delete=models.PROTECT),
    trip = models.ForeignKey('Shopping_trip', on_delete=models.PROTECT),  # might be unnecessary


class House_manager(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT),
    house = models.ForeignKey('House', on_delete=models.PROTECT),


class Manager_meeting(models.Model):
    date = models.DateField(),
    location = models.CharField(max_length=50)
    minutes_discussed = models.BooleanField()


class Attendee(models.Model):
    meeting = models.ForeignKey('Manager_meeting', on_delete=models.PROTECT),
    manager = models.ForeignKey('House_manager', on_delete=models.PROTECT),


class Site_visit(models.Model):
    date = models.DateField(),
    issues = models.TextField(null=True),
    conductor = models.ForeignKey('House_manager', on_delete=models.PROTECT),
    house = models.ForeignKey('House', on_delete=models.PROTECT),


class Manager_issue(models.Model):
    description = models.CharField(max_length=200)
    STATUS_CHOICES = [
        ('n', 'New'),
        ('o', 'Ongoing')
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, null=True)
    expected_completion = models.DateField(),
    meeting = models.ForeignKey('Manager_meeting', on_delete=models.PROTECT),  # automatic


class Check_in(models.Model):
    date = models.DateField(),
    METHOD_CHOICES = [
        ('ip', 'In person'),
        ('pc', 'Phone call'),
        ('tx', 'Text')
    ]
    method = models.CharField(max_length=2, choices=METHOD_CHOICES)
    notes = models.TextField(null=True),
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT),
    conductor = models.ForeignKey('House_manager', on_delete=models.PROTECT),


class House_meeting(models.Model):
    date = models.DateField(),
    issues = models.TextField(null=True),
    house = models.ForeignKey('House', on_delete=models.PROTECT),
    conductor = models.ForeignKey('House_manager', on_delete=models.PROTECT),


class Absentee(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.PROTECT),
    meeting = models.ForeignKey('House_meeting', on_delete=models.PROTECT),  # automatic