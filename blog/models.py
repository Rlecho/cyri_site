from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True)
    content = models.TextField(verbose_name="Contenu")
    excerpt = models.TextField(max_length=500, verbose_name="Extrait")
    image = models.ImageField(upload_to='articles/images/', blank=True, null=True, verbose_name="Image")
    file = models.FileField(upload_to='articles/files/', blank=True, null=True, verbose_name="Fichier à télécharger")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def get_download_count(self):
        return self.downloads.count()

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="Article")
    author_name = models.CharField(max_length=100, verbose_name="Nom")
    author_email = models.EmailField(verbose_name="Email")
    content = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Commentaire de {self.author_name} sur {self.article.title}"

class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies', verbose_name="Commentaire")
    author_name = models.CharField(max_length=100, default="Admin", verbose_name="Auteur")
    content = models.TextField(verbose_name="Réponse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Réponse de {self.author_name}"

class Download(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='downloads', verbose_name="Article")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    downloaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de téléchargement")
    
    class Meta:
        verbose_name = "Téléchargement"
        verbose_name_plural = "Téléchargements"
    
    def __str__(self):
        return f"Téléchargement de {self.article.title}"

        

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message de {self.name} - {self.subject}"