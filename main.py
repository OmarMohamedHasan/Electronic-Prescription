from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
import sys

from windows.login_window import LoginWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load Noto Sans Arabic font
    font_id = QFontDatabase.addApplicationFont("assets/NotoSansArabic-Regular.ttf")
    if font_id != -1:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(family, 11))
    else:
        print("⚠️ لم يتم تحميل خط NSA")

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

from database.db_init import update_database

update_database()

