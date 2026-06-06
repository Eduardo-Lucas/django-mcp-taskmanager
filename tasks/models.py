from django.db import models

class Task(models.Model):
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('doing', 'In Progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Unknown')

    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Unknown')
    
    def __str__(self):
        return f"{self.title} (Status: {self.get_status_display()}) - Priority: {self.get_priority_display()}"
