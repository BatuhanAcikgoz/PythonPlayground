from flask import url_for


def get_profile_image(user):
    """
    Get the profile image URL for a user.
    If the user has a custom image, return that. Otherwise, return the default image.
    """
    if user.profile_image:
        return url_for('static', filename='profile_images/' + user.profile_image)
    else:
        return url_for('static', filename='profile_images/default.png')