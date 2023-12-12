import flet as ft
import sqlite3
import random


class DataBaseController:
    @classmethod
    def connect(cls, query):
        with sqlite3.connect('assets/database/database.db') as db:
            cursor = db.cursor()
            cursor.execute(query)
            result = [item for item in cursor]
            db.commit()
        return result

    @classmethod
    def get_item(cls, index):
        query = f''' SELECT * FROM ITEMS WHERE Id = {index}'''
        result = cls.connect(query)
        return result[0]

    @classmethod
    def call(cls, selected, table, equal=None, condition=None):
        if equal is None:
            return cls.connect(f''' SELECT {selected} FROM {table}''')
        else:
            return cls.connect(f''' SELECT {selected} FROM {table} WHERE {equal} = {condition}''')


class Item(ft.Tooltip):
    def __init__(self, name, img, addition):
        super().__init__(message=name)
        self.img = img
        self.addition = addition
        self.content: ft.Container = ft.Container(
            padding=ft.padding.only(left=3),
            content=ft.Text(value=self.addition, size=20, color=ft.colors.WHITE, font_family='PW'),
            alignment=ft.alignment.bottom_left,
            height=50,
            width=50,
            bgcolor=ft.colors.BLACK54,
            image_src=self.img,
            image_fit='FILL'
        )


class Elements(ft.SafeArea):
    def __init__(self, page: ft.Page):
        super().__init__(minimum=10, maintain_bottom_view_padding=True)
        self.page = page
        self.loot = list()
        self.chances = dict()
        self.title: ft.Text = ft.Text('Симулятор сундуков Perfect World', size=20, weight='w800')
        self.box_dropdown: ft.Dropdown = ft.Dropdown(
            hint_text='Какой сундук открываем?',
            on_change=self.choice,
            options=[ft.dropdown.Option(i[0]) for i in DataBaseController.call('NAME', 'lootboxes')]
        )
        self.inventory: ft.GridView = ft.GridView(
            width=self.page.width,
            height=self.page.height * 0.65,
            max_extent=50,
            child_aspect_ratio=1
        )
        self.button: ft.ElevatedButton = ft.ElevatedButton(text='Открыть сундук',
                                                           on_click=self.open,
                                                           width=page.width,
                                                           height=50)
        self.main: ft.Stack = ft.Stack(
            controls=[
                ft.Container(content=self.button,
                             alignment=ft.alignment.bottom_center,
                             height=page.height - self.button.height),
                ft.Column(
                    controls=[
                        ft.Row(controls=[self.title]),
                        ft.Divider(height=20),
                        ft.Divider(height=10, color='transparent'),
                        self.box_dropdown,
                        self.inventory
                    ]
                )
            ]
        )
        self.content = self.main

    def choice(self, e):
        box = DataBaseController.call('database_name', 'lootboxes', 'name', f"'{self.box_dropdown.value}'")[0][0]
        self.chances = {key: value for key, value in DataBaseController.call('*', box)}
        self.inventory.controls.clear()
        self.inventory.update()
        self.loot.clear()

    def open(self, e):
        if self.box_dropdown.value is None:
            return
        loot_id = {random.choices(list(self.chances.keys()), weights=list(self.chances.values()))[0]}
        index, name, img, addition = DataBaseController.get_item(*loot_id)
        item = Item(name, img, addition)
        for i in range(len(self.inventory.controls)):
            if self.inventory.controls[i].content.image_src in self.loot:
                continue
            self.loot.append(self.inventory.controls[i].content.image_src)
        if img in self.loot:
            self.inventory.controls[self.loot.index(img)].content.content.value += addition
        else:
            self.inventory.controls.append(item)
        self.inventory.update()


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {'PW': 'fonts/fzl2jw.ttf'}

    elements: object = Elements(page)
    page.add(elements)


if __name__ == '__main__':
    ft.app(target=main, assets_dir='assets', view=ft.AppView.WEB_BROWSER)
