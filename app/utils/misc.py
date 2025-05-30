from flask import url_for


def get_profile_image(user):
    """

    """
    if user.profile_image:
        return url_for('static', filename='profile_images/' + user.profile_image)
    else:
        return url_for('static', filename='profile_images/default.png')