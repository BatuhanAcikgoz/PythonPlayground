from app.models.base import db


class Badges(db.Model):
    """
    Represents a badge entity within the database.

    This class maps to the "badges" table in the database and is used to store
    information about various badges. It includes details such as the unique name,
    description, icon path, color, and timestamps for creation and updates.

    Attributes:
        id: A unique identifier for the badge.
        name: The unique name of the badge.
        description: A descriptive text providing information about the badge.
        icon: The file path to the badge's icon image.
        color: The hex code representing the badge's color.
        created_at: The timestamp indicating when the badge was created.
        updated_at: The timestamp indicating when the badge was last updated.
    """
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # Path to the icon file
    color = db.Column(db.String(7), nullable=False)  # Hex color code
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        """
        Bir rozet nesnesi için temsil edici bir dize döndüren metod.

        Returns
        -------
        str
            Rozet adını içeren bir dize döner.
        """
        return f'<Badge {self.name}>'