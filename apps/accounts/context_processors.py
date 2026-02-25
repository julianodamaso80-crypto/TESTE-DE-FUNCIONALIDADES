def user_preferences(request):
    if request.user.is_authenticated:
        return {
            'ui_theme': request.user.ui_theme,
            'ui_density': request.user.ui_density,
        }
    return {'ui_theme': 'dark', 'ui_density': 'comfortable'}
