import os
import tensorflow as tf
from dataflow import time

class Checkpoint(object):
    def __init__(
            self,
            saved_vars=None,
            save_path=None,
            max_to_keep=1,
            n_second_save=None,
            n_steps_save=None,
            save_steps = True,
    ):
        self._save_path = save_path or 'model'
        self._saved_vars = saved_vars or {}
        self._max_to_keep = max_to_keep
        self._n_second_save = n_second_save
        self._n_steps_save = n_steps_save
        self._save_steps = save_steps


        # state
        self._last_saved_time = time.time()
        self._last_saved_step = 0
        self._t_steps = tf.Variable(0, dtype=tf.int64)

        # save steps
        if self._save_steps: self.add_saved_vars(__checkpoint_steps__ = self._t_steps)


    @property
    def steps(self): return self._t_steps.numpy()


    def tick(self):

        # update steps
        steps = self._t_steps.assign_add(1)

        # check save condition
        if (self._n_second_save is not None and time.time() - self._last_saved_time >= self._n_second_save) or \
            (self._n_steps_save is not None and steps - self._last_saved_step >= self._n_steps_save):
            self.save()


    def save(self):
        # update states
        self._last_saved_step = self.steps
        self._last_saved_time = time.time()

        # check path exist
        os.makedirs(self._save_path, exist_ok=True)

        # save
        _, manager = self._get_tf_checkpoint_and_manager()
        manager.save()


    def restore(self):
        ckpt, manager = self._get_tf_checkpoint_and_manager()
        ckpt.restore(manager.latest_checkpoint)


    def add_saved_vars(self, **vars):
        # save vars
        for k, v in vars.items(): self._saved_vars[k] = v

        # reset checkpoint and manager
        self.__checkpoint = self.__checkpoint_manager = None


    def _get_tf_checkpoint_and_manager(self):
        if not hasattr(self, '_checkpoint'): self._checkpoint = tf.train.Checkpoint(**self._saved_vars)
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = tf.train.CheckpointManager(
                self._checkpoint,
                self._save_path,
                max_to_keep=self._max_to_keep,
            )
        return self._checkpoint, self._checkpoint_manager