"""
Módulo de modelos para la aplicación.

Este módulo define las clases de modelos necesarias para gestionar preguntas,
respuestas y retroalimentación de usuarios.

Clases de Modelos:
    - Question: Modelo que representa una preguntaa.
    - Answer: Modelo que representa una respuesta a una pregunta.
    - QuestionFeedback: Modelo que representa la retroalimentación de un 
      usuario a una pregunta.

Atributos Comunes:
    - created (DateField): Fecha de creación de la pregunta.
    - author (ForeignKey): Relación con el modelo de usuario que crea la pregunta.
    - title (CharField): Título de la pregunta.
    - description (TextField): Descripción detallada de la pregunta.
    - ranking (PositiveIntegerField): Puntuación de la pregunta basada en 
      respuestas y retroalimentación.

"""

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class Question(models.Model):
    """
    Modelo que representa una pregunta en la encuesta.

    Métodos:
        - get_absolute_url(): Devuelve la URL absoluta para ver y editar la pregunta.
    """

    created = models.DateField("Creada", auto_now_add=True)
    author = models.ForeignKey(
        get_user_model(),
        related_name="questions",
        verbose_name="Pregunta",
        on_delete=models.CASCADE,
    )
    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descripción")
    ranking = models.PositiveIntegerField("Ranking", default=0)

    objects = models.Manager()

    def get_absolute_url(self):
        return reverse("survey:question-edit", args=[self.pk])


class Answer(models.Model):
    """
    Modelo que representa una respuesta a una pregunta en la encuesta.

    Atributos Adicionales:
        - ANSWERS_VALUES (tuple): Elecciones posibles para el campo 'value'.
    """

    ANSWERS_VALUES = (
        (0, "Sin Responder"),
        (1, "Muy Bajo"),
        (2, "Bajo"),
        (3, "Regular"),
        (4, "Alto"),
        (5, "Muy Alto"),
    )

    question = models.ForeignKey(
        Question,
        related_name="answers",
        verbose_name="Pregunta",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        get_user_model(),
        related_name="answers",
        verbose_name="Autor",
        on_delete=models.CASCADE,
    )
    value = models.PositiveIntegerField("Respuesta", default=0)
    comment = models.TextField("Comentario", default="", blank=True)

    objects = models.Manager()


class QuestionFeedback(models.Model):
    """
    Modelo que representa la retroalimentación de un usuario a una pregunta.

    Atributos Adicionales:
        - value (TextField): Campo para almacenar la retroalimentación del usuario.
    """

    question = models.ForeignKey(
        Question,
        related_name="feedback",
        verbose_name="Pregunta",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        get_user_model(),
        related_name="feedback",
        verbose_name="Autor",
        on_delete=models.CASCADE,
    )
    value = models.TextField("Feedback", default="", blank=True)

    objects = models.Manager()
