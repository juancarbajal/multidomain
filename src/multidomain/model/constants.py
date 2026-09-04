"""Module of constants in database."""


class Constants:
    """Constants."""

    MULTIDOMAIN_STATE_INITIATED = 'initiated'
    MULTIDOMAIN_STATE_CREATED_ROUTE53 = 'route53_created'
    MULTIDOMAIN_STATE_CREATED_TUCOWS = 'tucows_created'
    MULTIDOMAIN_STATE_CREATED_ACM = 'acm_created'
    MULTIDOMAIN_STATE_UPDATED_ROUTE53 = 'route53_updated'
    MULTIDOMAIN_STATE_VALIDATED_ACM = 'acm_validated'
    MULTIDOMAIN_STATE_CREATED_CLOUDFRONT = 'cloudfront_created'
    MULTIDOMAIN_STATE_FINISHED = 'finished'
    MULTIDOMAIN_STATE_CANCEL = 'cancel'
