from django.db import models


class Page(models.Model):
    slug = models.SlugField(
        'Идентификатор',
        max_length=50,
        unique=True
    )
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    updated_at = models.DateTimeField(
        'Обновлено',
        auto_now=True
    )

    class Meta:
        verbose_name = 'страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.title
