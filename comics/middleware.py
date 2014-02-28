import datetime

from comics.models import (
    ReferralCode,
    ReferralHit,
)

class ReferralMiddleware(object):
    """
    Not currently using this, but it stands as an example if we ever
    get and actual referral systme in place.

    def process_response(self, request, response):

        if not request.COOKIES.get('ref_code_tracked'):

            ref_query = request.GET.get('r')

            if ref_query:
                try: 
                    code = ReferralCode.objects.get(
                        code=ref_query,
                        is_active=True,
                    )
                    ReferralHit.objects.create(
                        code=code,
                    )
                    response.set_cookie('ref_code_tracked', 'true')
                except ReferralCode.DoesNotExist:
                    pass

        return response

    """
    pass