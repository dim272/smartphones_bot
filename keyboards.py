from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data import *

'''

[Apple] > [iPhone 11] > [128]
[Xiaomi] > [Redmi Note 9] > [4] > [64]

'''


class Choice:
    def __init__(self):
        self.__page = 1
        self._items_used = 0

    def __get_len_items(self):
        return len(self.items)

    def __rows_we_need(self):
        num = self.__get_len_items()

        if num % 3 != 0:
            result = (num // 3) + 1
        else:
            result = int(num / 3)

        return result

    @staticmethod
    def _breadcrumbs_button_generator(select, item):
        cd = f'select:{select.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    def __button_generator(self, item):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    @staticmethod
    def __error_button():
        return InlineKeyboardButton(text='Ошибка', callback_data='select:control:item:start')

    @staticmethod
    def _start_button():
        return InlineKeyboardButton(text='< Начало', callback_data='select:control:item:start')

    def __next_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:next'
        btn = InlineKeyboardButton(text='>', callback_data=cd)
        return btn

    def __prev_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:prev'
        btn = InlineKeyboardButton(text='<', callback_data=cd)
        return btn

    def __breadcrumbs_row_generator(self):
        class_name = self.__class__.__name__
        breadcrumbs_row = []

        if class_name != 'Brand':
            start_button = self._start_button()
            breadcrumbs_row.append(start_button)
            brand_name = self.brand
            brand_button = self._breadcrumbs_button_generator('brand', brand_name)
            breadcrumbs_row.append(brand_button)
            if class_name == 'Ram':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
            if class_name == 'Storage':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
                ram = self.ram
                ram_button = self._breadcrumbs_button_generator('ram', ram)
                breadcrumbs_row.append(ram_button)

        return breadcrumbs_row

    def __row_generator(self, row_number):
        row = []
        counter = 1
        while counter <= 3 and self._items_used < self.__get_len_items():
            item = self.items[self._items_used]
            btn = self.__button_generator(item)

            if counter == 1:
                if row_number == 1:
                    if self._items_used == 0:
                        row.append(btn)
                        counter += 1
                        self._items_used += 1
                    else:
                        row.append(self.__prev_page_button())
                        counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            elif counter == 2:
                row.append(btn)
                counter += 1
                self._items_used += 1
            elif counter == 3:
                if row_number == 3 and self._items_used == (self.__get_len_items() - 1):
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
                elif row_number == 3:
                    row.append(self.__next_page_button())
                    counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            else:
                row.append(self.__error_button())
                counter += 1

        return row

    def keyboard_generator(self):
        inline_keyboard = []
        breadcrumbs = self.__breadcrumbs_row_generator()
        row_number = 1

        if breadcrumbs:
            inline_keyboard.append(breadcrumbs)

        if self.__rows_we_need() > 3:
            rows_we_need = 3
        else:
            rows_we_need = self.__rows_we_need()

        while row_number <= rows_we_need:
            row = self.__row_generator(row_number)
            inline_keyboard.append(row)
            row_number += 1

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return keyboard

    def next_page(self):
        self.__page += 1

    def prev_page(self):
        if self.__page != 1:
            self.__page -= 1
            if self.__page == 1:
                self._items_used -= 15
            else:
                self._items_used -= 14
        else:
            self._items_used -= 8


class Brand(Choice):
    def __init__(self):
        self.items = self.__get_top_brands()
        super().__init__()

    @staticmethod
    def __get_top_brands():
        db = TopBrands
        select = db.select(db.brand).order_by(db.top.desc())
        brand_list = []
        for each in select:
            brand_list.append(each.brand)
        return brand_list

    @staticmethod
    def increase_top_value(brand_name):
        db = TopBrands
        try:
            select = db.get(db.brand.contains(brand_name.strip()))
            top = select.top
            top += 1
            select.update(top=top).where(db.brand == select.brand).execute()
        except DoesNotExist:
            db.create(brand=brand_name, top=1)


class Model(Choice):
    def __init__(self, brand):
        self.brand = brand
        self.items = self.__get_models()
        super().__init__()

    def __get_models(self):
        db = Smartphones
        select = db.select(db.model).where(db.brand == self.brand.strip()).order_by(db.top.desc())
        model_list = []
        for each in select:
            model = each.model
            if model not in model_list:
                model_list.append(model)

        return model_list

    @staticmethod
    def increase_top_value(model_name):
        db = Smartphones
        try:
            select = db.get(db.model.contains(model_name.strip()))
            top = select.top

            try:
                top += 1
            except TypeError:
                top = 1
            select.update(top=top).where(db.id == select.id).execute()
        except DoesNotExist:
            pass


class Ram(Choice):
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self.items = self.__get_ram()
        super().__init__()

    def __get_ram(self):
        db = Smartphones
        select = db.select(db.ram).where(db.brand == self.brand.strip(), db.model == self.model.strip())
        ram_list = []
        for each in select:
            try:
                ram = each.ram
            except:
                continue
            if ram not in ram_list:
                ram_list.append(ram)

        return ram_list


class Storage(Choice):
    def __init__(self, brand, model, ram):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.items = self.__get_storage()
        super().__init__()

    def __get_storage(self):
        db = Smartphones

        if self.ram:
            select = db.select(db.storage).where(db.brand == self.brand.strip(),
                                                 db.model == self.model.strip(),
                                                 db.ram == self.ram.strip())
        else:
            select = db.select(db.storage).where(db.brand == self.brand.strip(),
                                                 db.model == self.model.strip())
        storage_list = []
        for each in select:
            try:
                storage = each.storage
            except:
                continue
            if storage not in storage_list:
                storage_list.append(storage)

        return storage_list


class Breadcrumbs(Choice):
    def __init__(self, ):
        super().__init__()

    def breadcrumbs_keyboard(self, brand, model, ram, storage):
        values = [['brand', brand], ['model', model], ['ram', ram], ['storage', storage]]
        specifications = []
        for val in values:
            if val[1]:
                specifications.append([f'{val[0]}', val[1]])

        breadcrumbs = []
        start_button = self._start_button()
        breadcrumbs.append(start_button)
        for each in specifications:
            select = each[0]
            item = each[1]
            button = self._breadcrumbs_button_generator(select, item)
            breadcrumbs.append(button)

        return breadcrumbs


class FinaleKeyboard(Breadcrumbs):

    def __init__(self):
        super().__init__()

    def links_to_markets(self):
        db = Smartphones
        search = db.select().where(db.id == self.id)
        links = {}

        if search:
            for item in search:
                ekatalog = item.url_ekatalog
                if ekatalog:
                    links['E-Katalog'] = ekatalog
                avito = item.url_avito
                if avito:
                    links['Avito'] = avito
                youla = item.url_youla
                if youla:
                    links['Youla'] = youla

        return links

    @staticmethod
    def market_button_generator(name, link):
        return InlineKeyboardButton(text=name, url=link)

    def generate(self):
        breadcrumbs = self.breadcrumbs_keyboard(self.brand, self.model, self.ram, self.storage)
        inline_keyboard = [breadcrumbs]

        links = self.links_to_markets()
        if links:
            links_block = []
            for item in links:
                link = links.get(item)
                market_button = self.market_button_generator(item, link)
                links_block.append(market_button)
            inline_keyboard.append(links_block)

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        return keyboard


class Info:

    def __init__(self):
        self.id = None

    def _first_row_generator(self):
        if self.ram and self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}/{self.storage}'
        elif self.ram and not self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}'
        elif (not self.ram and self.storage) or self.brand == 'Apple':
            first_row = f'{self.brand} {self.model} {self.storage}'
        else:
            first_row = f'{self.brand} {self.model}'

        return first_row

    def _get_specifications_from_db(self):
        db = Smartphones
        specifications = db.select().where(db.brand == self.brand, db.model == self.model,
                                           db.ram == self.ram, db.storage == self.storage)

        spec_dict = specifications.dicts().execute()
        result = {}
        for item in spec_dict:
            result = {**result, **item}
        return result

    @staticmethod
    def _specifications_text_generator(block_list):
        text = row = ''
        len_row = 40

        for item in block_list:
            item = item[0]
            item_plus = ''
            if len(row) > 0:
                item_plus = '   ' + item

            try:
                if item_plus:
                    row2 = row + item_plus
                else:
                    row2 = row + item

                if len(row2) <= len_row:
                    row = row2
                    continue
                else:
                    raise ValueError
            except ValueError:
                text += f'{row}\n'
                row = item

        if row not in text:
            text += f'{row}\n'

        return text

    def _specifications_block_generator(self, specifications):
        keys = {'release': 'Релиз:', 'os': 'ОС:', 'display': 'Экран:', 'cpu': 'Процессор:',
                'cpu_num': 'Количество ядер:', 'core_speed': 'Такт. частота:', 'battery': 'Ёмкость аккум.:',
                'weight': 'Вес:', 'dimensions': 'Габариты (мм):'}

        values = {'release': 'г.', 'display': '"', 'cpu_num': 'шт.', 'core_speed': 'МГц/ГГц',
                  'battery': 'мАч', 'weight': 'гр.'}

        block_list = []

        for row in specifications:

            if not specifications[row]:
                continue

            if row in keys.keys():

                key = keys[row]
                val = specifications[row]

                if row in values:
                    after_value = values[row]
                    if row == 'core_speed':
                        try:
                            experiment_val = float(val)
                            if experiment_val > 10.0:
                                after_value = 'МГц'
                            else:
                                after_value = 'ГГц'
                        except ValueError:
                            after_value = 'МГц'

                    val = f'{val} {after_value}'

                block_list.append([f'{key} {val}'])

        text = self._specifications_text_generator(block_list)

        if specifications['in_stock']:
            in_stock = 'Есть в продаже'
        else:
            in_stock = 'Нет в продаже'

        text += in_stock

        return text

    def specifications(self):
        specifications = self._get_specifications_from_db()
        self.id = smart_id = specifications['id']
        img = specifications['img']

        message = f'{self._first_row_generator()}\n'
        message += self._specifications_block_generator(specifications)

        prices = self.prices(smart_id)

        if prices:
            for row in prices:
                message += f'\n{row}'

        return {'text': message, 'img': img, 'smartphone_id': smart_id}

    @staticmethod
    def prices(smartphone_id):
        prices_table = Prices

        try:
            prices = prices_table.select().where(prices_table.smartphone_id == smartphone_id)
        except DoesNotExist:
            prices = []

        prices2_table = PricesSecondMarkets

        try:
            prices2 = prices2_table.select().where(prices2_table.smartphone_id == smartphone_id)
        except DoesNotExist:
            prices2 = []

        ozon = yandex = mvideo = eldorado = citilink = svyaznoy = \
            aliexpress = megafon = mts = sber = avito = youla = ''

        message = []

        for item in prices:
            ozon = item.ozon
            yandex = item.yandex
            mvideo = item.mvideo
            eldorado = item.eldorado
            citilink = item.citilink
            svyaznoy = item.svyaznoy
            megafon = item.megafon
            mts = item.mts
            sber = item.sber_mm
            aliexpress = item.aliexpress

        for item in prices2:
            avito = item.avito
            youla = item.youla

        if ozon:
            row = f'Озон: {ozon} р'
            message.append(row)

        if yandex:
            row = f'Яндекс: {yandex} р'
            message.append(row)

        if mvideo:
            row = f'М-Видео: {mvideo} р'
            message.append(row)

        if eldorado:
            row = f'Эльдорадо: {eldorado} р'
            message.append(row)

        if citilink:
            row = f'Citilink: {citilink} р'
            message.append(row)

        if svyaznoy:
            row = f'Связной: {svyaznoy} р'
            message.append(row)

        if megafon:
            row = f'Мегафон: {megafon} р'
            message.append(row)

        if mts:
            row = f'МТС: {mts} р'
            message.append(row)

        if aliexpress:
            row = f'AliExpress: {aliexpress} р (возможно не новый)'
            message.append(row)

        if sber:
            row = f'СберМегаМаркет: {sber} р'
            message.append(row)

        if avito:
            row = f'Авито: {avito} р (средняя)'
            message.append(row)

        if youla:
            row = f'Юла: {youla} р (средняя)'
            message.append(row)

        if message:
            message.insert(0, '-------- цены --------')

        return message

    def avito_youla_update(self):
        pass
        # a = Avito(self.brand, self.model, self.storage, self.ram)
        # y = Youla(self.brand, self.model, self.storage, self.ram)
        # avito_parsing = a.data_mining()
        # youla_parsing = y.data_mining()
        # result = {**avito_parsing, **youla_parsing}
        # return result

    # добавить результат в базу смартфонов с екаталога "smarphones"
    # если происходит парсинг, реализовать выдачу последовательную выдачу финального сообщения:
    # сперва то, что есть в базе (характеристики и имг), после парсинга цены


class FinaleMessage(Info, FinaleKeyboard):
    def __init__(self, brand, model, ram, storage, smartphone_id=None):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.storage = storage
        self.id = smartphone_id
        super().__init__()
