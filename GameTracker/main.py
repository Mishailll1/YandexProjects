import sys
from PyQt6.QtWidgets import QApplication, QInputDialog, QMessageBox, QFileDialog
from ui import GameTrack
import db_control
import steam_service

class MainWindow(GameTrack):
    def __init__(self):
        super().__init__()
        db_control.init_db()

        self.curr_idx = 0
        self.game_list = db_control.get_appids()
        saved_steamid = db_control.get_id()
        self.steamid = saved_steamid if saved_steamid else ''
        self.curr_appid = None
        self.curr_status = None

        self.add.clicked.connect(self.save_to_db)
        self.NextBut.clicked.connect(self.next_game)
        self.PreviousBut.clicked.connect(self.prev_game)
        self.add_id.clicked.connect(self.add_steam)
        self.add_many.clicked.connect(self.add_from_txt)
        self.refreshed.clicked.connect(self.refresh)
        self.delete_game.clicked.connect(self.delete)
        self.tags.currentTextChanged.connect(self.on_status_changed)

        if not self.game_list:
            pass
        else:
            self.load_game(self.curr_idx)

    def save_to_db(self):
        if not self.steamid:
            QMessageBox.warning(self,
                                'Ошибка',
                                'SteamID пуст. Добавь его.')
            return
        app, ok = QInputDialog.getText(self,
                                       "Ввод",
                                       "Введи appid игры:")
        if not (ok and app.isdigit()):
            return

        appid = int(app)
        game_info = steam_service.get_info(appid)
        if not game_info:
            QMessageBox.warning(self,
                                'Ошибка',
                                'Такой игры не найдено.')
            return

        name, header = game_info['name'], game_info['thumbnail']
        hours = steam_service.get_hours(self.steamid, appid)
        ach_data = steam_service.get_achievements(int(self.steamid), appid)

        curr_ach = 0
        total_ach = 0
        if ach_data:
            curr_ach = ach_data['curr_ach']
            total_ach = ach_data['total_ach']

        db_control.add_game(appid, game_info['name'], game_info['thumbnail'])
        db_control.update_stats(appid, hours, curr_ach, total_ach)

        print(f'{game_info["name"]} добавлена.')

        self.game_list = db_control.get_appids()
        self.curr_idx = self.game_list.index(appid)
        self.load_game(self.curr_idx)

    def update_screen(self, name, curr_ach, total_ach, hoursG, headerG, status=None, appid=None):
        print(f"Обновляем экран. Статус из БД: {status}")
        self.name.setText(name)
        if headerG:
            self.load_img(headerG)

        hours = hoursG
        self.hours.setText(f"{str(hours)} ч.")
        self.achivements.setText(f'Достижений: {curr_ach}/{total_ach}')
        if status:
            final_status = status
            if status == 'Пройдено!':
                color = 'green'
            elif status == 'Платина!💎':
                color = '#00bfff'
            elif status == 'Не начата':
                color = 'gray'
            else:
                color = 'orange'
        elif total_ach > 0 and curr_ach == total_ach:
            final_status = 'Платина!💎'
            color = '#00bfff'
        elif hours > 0:
            final_status = 'В процессе'
            color = 'green'
        else:
            final_status = 'Не начата'
            color = 'gray'
        print(f'Цвет: {color}')
        self.status.setText(final_status)
        self.status.setStyleSheet(f'color: {color}')

        if self.tags.currentText() != final_status:
            self.tags.blockSignals(True)
            self.tags.setCurrentText(final_status)
            self.tags.blockSignals(False)
        if appid and final_status in ['Платина!💎', 'Пройдено!', 'Заброшено']:
            db_control.set_status(appid, final_status)

    def load_game(self, idx):
        appid = self.game_list[idx]
        game_data = db_control.get_game_fromdb(appid)
        db_status = game_data[1]

        if db_status:
            self.tags.blockSignals(True)
            self.tags.setCurrentText(db_status)
            self.tags.blockSignals(False)

        self.curr_status = db_status
        self.curr_appid = appid

        self.update_screen(game_data[0],
                           game_data[3],
                           game_data[4],
                           game_data[2],
                           game_data[5],
                           status=game_data[1],
                           appid=appid)
        print(game_data)

    def add_steam(self):
        steam_id, ok = QInputDialog.getText(self,
                                      'Добавление ID',
                                      'Введи свой SteamID:')
        if ok and steam_id.isdigit() and steam_id.strip() != '':
            db_control.add_id(steam_id)
            self.steamid = steam_id
            QMessageBox.information(self,
                                    'Успех',
                                    'SteamID сохранён.')
        elif not ok:
            pass
        else:
            QMessageBox.warning(self,
                                'Ошибка',
                                'Проверь правильность SteamID.')

    def add_from_txt(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            'Выбери файл со списком AppID',
            '',
            'Text Files (*.txt)'
        )

        if not file:
            return

        try:
            with open(file, 'r', encoding='UTF-8') as f:
                data = f.read()
        except Exception as error:
            QMessageBox.warning(self,
                                'Ошибка',
                                f'Не удалось прочитать файл.\n{error}')
            return
        temp = data.replace('\n', ',').split(',')
        ids = [int(x.strip()) for x in temp if x.strip().isdigit()]
        if not ids:
            QMessageBox.warning(self,
                                'Внимание',
                                'В файле не найдено AppID.')
        self.list_add_games(ids)

    def delete(self):
        if not hasattr(self, 'curr_appid') or not self.curr_appid:
            QMessageBox.warning(self,
                                'Ошибка',
                                'Нет выбранной игры для удаления.')
        game_name = self.name.text()
        reply = QMessageBox.question(self,
                                     'Подтверждение удаления',
                                     f'Ты уверен, что хочешь удалить игру {game_name}?\n'
                                     f'Это действие нельзя отменить.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        db_control.delete_game(self.curr_appid)
        self.game_list = db_control.get_appids()
        if self.game_list:
            self.curr_idx = self.curr_idx % len(self.game_list)
            self.load_game(self.curr_idx)
        else:
            self.curr_idx = 0
            self.clear()

    def clear(self):
        self.name.setText("?")
        self.hours.setText("0 ч.")
        self.achivements.setText("Достижений: 0/0")
        self.status.setText("Не начата")
        self.status.setStyleSheet("color: gray;")
        self.header.clear()
        self.header.setText("Нет игр в базе")
        self.header.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.curr_appid = None

    def list_add_games(self, id_list):
        success = 0
        fail = 0
        steamid = self.steamid if self.steamid else ""
        try:
            for appid in id_list:
                game_info = steam_service.get_info(appid)
                if not game_info:
                    fail += 1
                    continue

                hours = 0.0
                curr_ach = 0
                total_ach = 0

                if steamid:
                    hours = steam_service.get_hours(steamid, appid)
                    ach_data = steam_service.get_achievements(int(steamid), appid)
                    if ach_data:
                        curr_ach = ach_data['curr_ach']
                        total_ach = ach_data['total_ach']

                db_control.add_game(appid, game_info['name'], game_info['thumbnail'])
                db_control.update_stats(appid, hours, curr_ach, total_ach)
                success += 1

            self.game_list = db_control.get_appids()
            if self.game_list and self.curr_idx == 0:
                self.load_game(0)

            QMessageBox.information(self,
                                    'Импорт завершён',
                                    f'Добавлено: {success}\nНе добавлено(ошибка, не найдено): {fail}')
        except Exception as error:
            QMessageBox.warning(self,
                                'Ошибка',
                                f'Что-то пошло не так:\n{error}')

    def refresh(self):
        if not hasattr(self, 'curr_appid') or not self.curr_appid:
            QMessageBox.warning(self,
                                'Ошибка',
                                'Добавь или выбери игру.')

            return
        if not self.steamid:
            QMessageBox.warning(self,
                                'Ошибка',
                                'Сначала добавь SteamID.')
            return

        appid = self.curr_appid

        try:
            hours = steam_service.get_hours(self.steamid, appid) or 0.0
            ach_data = steam_service.get_achievements(int(self.steamid), appid)

            curr_ach = ach_data.get('curr_ach', 0) if ach_data else 0
            total_ach = ach_data.get('total_ach', 0) if ach_data else 0

            db_control.update_stats(appid, hours, curr_ach, total_ach)

            self.load_game(self.curr_idx)

            QMessageBox.information(self,
                                    'Успешно',
                                    'Данные обновлены.')

        except Exception as error:
            QMessageBox.warning(self,
                                'Ошибка',
                                f'Не удалось обновить:\n{error}')
            return

    def on_status_changed(self, new):
        print(f"Выбран новый статус: {new}")
        self.curr_status = new

        if hasattr(self, 'curr_appid') and self.curr_appid:
            db_control.set_status(self.curr_appid, new)

            game_data = db_control.get_game_fromdb(self.curr_appid)
            self.update_screen(game_data[0],
                               game_data[3],
                               game_data[4],
                               game_data[2],
                               game_data[5],
                               status=new,
                               appid=self.curr_appid)

    def apply_status(self):
        if self.curr_appid and self.curr_status:
            db_control.set_status(self.curr_appid, self.curr_status)

    def next_game(self):
        if not self.game_list:
            return
        self.apply_status()
        self.curr_idx = (self.curr_idx + 1) % len(self.game_list)
        self.load_game(self.curr_idx)

    def prev_game(self):
        if not self.game_list:
            return
        self.apply_status()
        self.curr_idx = (self.curr_idx - 1) % len(self.game_list)
        self.load_game(self.curr_idx)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    sys.excepthook = except_hook
    win.show()
    sys.exit(app.exec())