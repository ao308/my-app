from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=100, default='No Name')
    title = models.CharField('タイトル', max_length=100, null=True, blank=True)
    subtitle = models.CharField('サブタイトル', max_length=100, null=True, blank=True)
    topimage = models.ImageField(upload_to= 'images', verbose_name='トップ画像')
    introduction = models.TextField('概要')
    proposal = models.CharField('企画書', max_length=100, null=True, blank=True)
    screendiagram = models.CharField('画面設計図', max_length=100, null=True, blank=True)
    screentransitiondiagram = models.CharField('画面遷移図', max_length=100, null=True, blank=True)
    ERdiagram = models.CharField('ER図', max_length=100, null=True, blank=True)
    myapp = models.CharField('フィットネスログアプリへ', max_length=100, null=True, blank=True)


    def __str__(self):
        return self.name

