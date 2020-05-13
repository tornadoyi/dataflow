import os
import tensorflow as tf

Dataset = tf.data.Dataset


def __element_loop_iterator(self):
    def iterator():
        while True:
            for d in self: yield d
    return iterator()


def __get_next(self):
    iter = getattr(self, '__iter_element_loop', None)
    if iter is None: iter = self.__iter_element_loop = self.element_loop_iterator()
    return next(iter)


Dataset.element_loop_iterator = __element_loop_iterator
Dataset.get_next = __get_next



