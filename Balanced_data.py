# -*- coding: utf-8 -*-
"""
Скрипт для балансировки данных, которые затем используются в обучении.
Для старта работы скрипта необходимо указать директорию, где хранятся изображения. Скрипт будет выполнять следующие
шаги:
1) Проверит все поддиректории в указанной директории и создаст связку имя поддиректории - количество картинок в ней
2) В зависимости от настроек может быть реализовано 3 типа подготовки данных:
    1) находится поддиректория с максимальным количеством картинок и в других директориях создаются такое же количество
   количество картинок
   2) рассчитывается суммарное количество картинок во всех директориях и затем вычислеятеся среднее количество картинок
   на 1 класс, путем деления этой суммы на количество классов
   3) находится поддиректория с минимальным количеством картинок, остальные картинки выбрасиваются из других директорий

ВАЖНО!!! Поддерживается лишь 1 уровень вложенности, если это будет необходимо, то данная функциональность будет
расширена.
"""
import os
import random
from skimage import data, transform, color, io, util
from skimage.filters import sobel


class BalancedData:
    def __init__(self, mode, root_folder_path):
        """
        :param mode: принимает одно из трёх значений max - для нормировки на максимально возможное количество
        изображений в классе, mean - количество данных берется по среднему, min - для нормировки на минимально возможное
        количесто изображений в классе
        :param root_folder_path: путь до корневой директории
        """
        self.mode = mode
        self.root_folder_path = root_folder_path

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, m):
        if not m: raise Exception("Attribute mode can't be empty.")
        if m not in ['max', 'mean', 'min']: raise Exception("Attribute m should receive only max, mean or min values.")
        self._mode = m

    @property
    def root_folder_path(self):
        return self._root_folder_path

    @root_folder_path.setter
    def root_folder_path(self, path):
        if not os.path.exists(path): raise Exception("Incorrect path to root folder.")
        self._root_folder_path = path

    def _get_data_list(self):
        """
        Возвращает список кортежей, где первый элемент кортежа это имя поддиректории, второе значение это количество
        элементов в данной поддиректории.
        :return:список кортежей
        """
        list_of_tuples = []
        for subfolder in os.listdir(os.path.join(self._root_folder_path)):
            current_tuple = (subfolder, len(os.listdir(os.path.join(self._root_folder_path, subfolder))))
            if len(list_of_tuples) == 0:
                list_of_tuples.append(current_tuple)
            else:
                for position_number in range(len(list_of_tuples)):
                    if current_tuple[1] <= list_of_tuples[position_number][1]:
                        list_of_tuples.insert(position_number, current_tuple)
                        break
                    if position_number == len(list_of_tuples) - 1:
                        list_of_tuples.append(current_tuple)
        return list_of_tuples

    def _get_value_to_normilize(self):
        """
        Возвращение значение на которое будет производится нормализация
        :return:целочисленное значение
        """
        full_data = self._get_data_list()
        if self._mode == 'min':
            return full_data[0][1]
        elif self._mode == 'max':
            return full_data[-1][1]
        else:
            return int(sum([int(im_numb[1]) for im_numb in full_data])/len(full_data))

    def _cout_data_to_change(self):
        """
        Возвращает список кортежей, где первый элемент кортежа это имя поддиректории, второй элемент это количество
        изображений, которое необходимо изменить, если значение отрицательно, тогда случайно удалаются значения, если
        равно 0, тогда ничего не делается, если положительное, тогда мы создаем новые данные, путём трансформации
        данных.
        :return:список кортежей
        """
        updated_list = []
        for value in self._get_data_list():
            updated_list.append((value[0], value[1]-self._get_value_to_normilize()))
        return updated_list

    #Ниже будет идти блок для работы с данными, удаление лишних или же создание новых изображений
    def delete_data(self, folder_name, amount_to_delete):
        """
        Метод для удаления лишних данных из директории в случайном порядке.
        :param folder_name: путь до папки в которой будет производится изменения данных
        :param amount_to_delete: количество данных, которое необходимо удалить
        :return:None
        """
        all_data = os.listdir(folder_name)
        random.shuffle(all_data)
        for i in range(amount_to_delete):
            try:
                os.remove(os.path.join(folder_name, all_data[i]))
            except FileNotFoundError as err:
                print(err)

    def picture_transformations(self, path_to_folder, pict_name):
        """
        Метод для создания цикла преобразований над изображением. Последовательно созадются следующие преобразования:
            1) преобразование из RGB to Grey
            2) инвертирование цвета
            3) поворот изображения на 90 градусов (90, 180, 270)
        :param path_to_folder: путь до папки в которую будут сохраняться изображения
        :param pict_name: название изменяемого изображения
        :return:None
        """
        original_pict = data.load(os.path.join(path_to_folder, pict_name))
        io.imsave(os.path.join(path_to_folder, pict_name.split(".")[0] + "_grey.jpg"), color.rgb2grey(original_pict))
        io.imsave(os.path.join(path_to_folder, pict_name.split(".")[0] + "_invert_color.jpg"), util.invert(original_pict))
        for angle in [90, 180, 270]:
            io.imsave(os.path.join(path_to_folder, pict_name.split(".")[0] + "_angle_{0}.jpg".format(angle)),
                      transform.rotate(original_pict, angle))
        io.imsave(os.path.join(path_to_folder, pict_name.split(".")[0] + "_sobel.jpg"),
                  sobel(color.rgb2grey(original_pict)))

    def create_new_data(self, path_to_folder, amount_to_create):
        """
        Метод для создания новых данных.
        :param path_to_folder: папка в которую будут сохраняться данные
        :param amout_to_create: количество данных, которое необходимо создать
        :return:None
        """
        while amount_to_create >= 0:
            for pict_name in os.listdir(path_to_folder):
                self.picture_transformations(path_to_folder, os.path.join(path_to_folder, pict_name))
                amount_to_create = amount_to_create - 6
                if amount_to_create <= 0:
                    break

    def balance(self):
        """
        Основной метод для работы с данными. Работает со списком кортежей и последовательно применяет методы для
        нормировки данных
        :return:
        """
        for tuple_data in self._cout_data_to_change():
            if tuple_data[1] < 0:
                print(tuple_data)
                self.create_new_data(os.path.join(self._root_folder_path, tuple_data[0]), abs(tuple_data[1]))
            elif tuple_data[1] > 0:
                print(tuple_data)
                self.delete_data(os.path.join(self._root_folder_path, tuple_data[0]), abs(tuple_data[1]))


if __name__ == '__main__':
    balanced_data = BalancedData(mode='mean', root_folder_path=r'/media/antoneryomin/B4FC9D09FC9CC750/BALANCED_DATA/name')
    balanced_data.balance()