from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base import db

# User-role ilişki tablosu
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class Role(db.Model):
    """
    Role sınıfı, veritabanında bir rol modelini temsil eder.

    Bu sınıf, rolün kimliği, adı ve isteğe bağlı açıklamasını içeren bir veritabanı
    tablosu tanımlar. Uygulama boyunca erişilebilir rolleri yönetmek için
    kullanılır. Her bir rol, benzersiz bir ada sahiptir ve hem kimlik hem de ad
    alanları zorunludur.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        """
        Bir Role nesnesinin okunabilir temsili oluşturan __repr__ yöntemi. Yöntem,
        Role nesnesinin 'name' niteliğini kullanarak geriye bilgi verici bir
        string döndürür.

        Returns:
            str: Role nesnesinin okunabilir temsili.
        """
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    """
    Kullanıcı verilerini temsil eden bir model sınıfı.

    User sınıfı, kullanıcıya ait temel bilgileri, rollerini ve şifreleme işlemlerini
    yönetir. `UserMixin` özelliğiyle kimlik doğrulama işlemleri için gerekli
    metotlara sahiptir ve `db.Model` taban sınıfını kullanır. Bu sınıf, bir
    veritabanı tablosu olarak yapılandırılmış ve her kullanıcı nesnesi bir
    kayıt olarak saklanacak şekilde tasarlanmıştır.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0, nullable=False)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        """
        Şifre hash'ini oluşturup saklayan bir metot.

        Bu metot, verilen şifreyi hash'leyerek saklar. Şifre hash'i oluşturmak
        için kullanılacak algoritma ve fonksiyon `generate_password_hash` olarak
        belirlenmiştir. Şifre hash'i güvenli bir şekilde, ham şifreyi saklamadan
        işlenir ve `password_hash` değişkeninde saklanır. Metot, özellikle
        kullanıcı doğrulama işlemleri öncesinde şifrelerin güvenli bir şekilde
        saklanmasını sağlamak için tasarlanmıştır.

        Args:
            password (str): Kullanıcının ham şifresi. Hash'lenip saklanmak
            üzere işlenecektir.

        Returns:
            None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Parolayı hashlenmiş haliyle karşılaştırmak için kullanılan bir yöntem.

        Bu yöntem, kullanıcının verdiği parolayı daha önce kaydedilmiş hashlenmiş
        parola ile karşılaştırmak için kullanılabilir. Parolanın doğru olup
        olmadığını döner.

        Parameters
        ----------
        password : str
            Karşılaştırılacak kullanıcı parolası.

        Returns
        -------
        bool
            Parolanın hashlenmiş değeri ile eşleşip eşleşmediğini belirten bir bool
            değer.
        """
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        """
        Belirtilen kullanıcı rolleri arasında verilen rol adına sahip bir rolün bulunup bulunmadığını kontrol eden bir
        fonksiyon. Bir kullanıcının belirli bir role sahip olup olmadığını anlamak için kullanılır.

        Args:
            role_name: Kontrol edilecek rolün adı.

        Returns:
            bool: Kullanıcı belirtilen role sahipse True, aksi takdirde False döner.
        """
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        """
        Kullanıcının "admin" rolüne sahip olup olmadığını kontrol eder.

        Returns:
            bool: Kullanıcı "admin" rolüne sahipse True, aksi halde False.
        """
        return self.has_role('admin')

    def is_teacher(self):
        """
        Belirtilen kullanıcı için öğretmen olup olmadığını kontrol eden bir fonksiyon.

        Bu fonksiyon, kullanıcının yetkilerini analiz ederek, öğretmen veya yönetici
        yetkisine sahip olup olmadığını belirler.

        Returns:
            bool: Kullanıcının öğretmen ya da yönetici olup olmadığı bilgisini döner.
        """
        return self.has_role('teacher') or self.is_admin()
