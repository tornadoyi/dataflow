import progressbar as _progressbar


class Progressbar(_progressbar.ProgressBar):
    def __init__(self, name=None, updater=None, *args, **kwargs):
        if 'widgets' not in kwargs:
            kwargs['widgets'] = [
                '[{}] '.format(name) if name is not None else '',
                _progressbar.Bar(),
                ' Progress:',
                _progressbar.Percentage(format='%(percentage)3d%%'),
                ' (',
                _progressbar.Counter(format='%(value)02d/%(max_value)d'),
                ') ',
                _progressbar.Timer(),
            ]
        super(Progressbar, self).__init__(*args, **kwargs)

        # start if updater is set
        if updater is not None:
            self.start()
            while True:
                try:
                    updater(self)
                    if not self.finished: continue
                    self.finish()
                    break
                except Exception as e:
                    self.finish()
                    raise e


    @property
    def finished(self): return self.value >= self.max_value

    def tick(self): self.update(self.value + 1)


def start(*args, **kwargs): return Progressbar(*args, **kwargs)