import logging

class LoggingMiddleWare(object):

    def process_response(self, request, response):
        log_string = "path='%s' host=%s remote_addr=%s forwarded_for='%s' user_agent=%s status=%s" % (
            request.path,
            request.get_host(),
            request.META.get('REMOTE_ADDR', ''),
            request.META.get('HTTP_X_FORWARDED_FOR', ''),
            request.META.get('HTTP_USER_AGENT', ''),
            response.status_code,
        )
        loggly_logger = logging.getLogger('loggly_logs')
        loggly_logger.info(log_string)

        return response