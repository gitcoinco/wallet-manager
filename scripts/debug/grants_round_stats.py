from django.utils import timezone

from grants.models import *
from grants.models import Contribution, PhantomFunding
from grants.views import next_round_start, round_end

# total stats

start = next_round_start
end = round_end

contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True)
pfs = PhantomFunding.objects.filter(created_on__gt=start, created_on__lt=end)
total = contributions.count() + pfs.count()

contributors = len(set(list(contributions.values_list('subscription__contributor_profile', flat=True)) + list(pfs.values_list('profile', flat=True))))
amount = sum([float(contrib.subscription.amount_per_period_usdt) for contrib in contributions] + [float(pf.value) for pf in pfs])

print("contributions", total)
print("contributors", contributors)
print('amount', amount)


# new feature stats for round 5 

subs = Subscription.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=48))
subs = subs.filter(subscription_contribution__success=True)
print(subs.count())
print(subs.filter(num_tx_approved__gt=1).count())
print(subs.filter(is_postive_vote=False).count())
