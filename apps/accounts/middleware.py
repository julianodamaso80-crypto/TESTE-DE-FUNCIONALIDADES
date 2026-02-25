class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated
                and not request.user.onboarding_completed
                and not request.path.startswith('/auth/')
                and not request.path.startswith('/accounts/onboarding')
                and not request.path.startswith('/health')
                and not request.path.startswith('/static')
                and not request.path.startswith('/media')
                and not request.path.startswith('/admin')):
            from django.shortcuts import redirect
            return redirect('accounts:onboarding')
        return self.get_response(request)
