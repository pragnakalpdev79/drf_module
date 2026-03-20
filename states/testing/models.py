from django.db import models
import logging

logger = logging.getLogger('user')

STATE_REQUEST = "request"
STATE_WAITING = "waiting"
STATE_TO_AIRPORT = "to_airport"
STATE_TO_HOTEL = "to_hotel"
STATE_DROPPED_OFF = "dropped_off"

STATE_CHOICES = (
    (STATE_REQUEST, STATE_REQUEST),
    (STATE_WAITING, STATE_WAITING),
    (STATE_TO_AIRPORT, STATE_TO_AIRPORT),
    (STATE_TO_HOTEL, STATE_TO_HOTEL),
    (STATE_DROPPED_OFF, STATE_DROPPED_OFF),
)

TRANSITIONS = {
    STATE_REQUEST: [STATE_WAITING,],
    STATE_WAITING: [STATE_REQUEST, STATE_TO_AIRPORT],
    STATE_TO_AIRPORT: [STATE_TO_HOTEL, STATE_REQUEST],
    STATE_TO_HOTEL: [STATE_DROPPED_OFF],
    STATE_DROPPED_OFF: [],
}

class PickUp(models.Model):
    __current_state = None

    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default=STATE_REQUEST
    )
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,*kwargs)
        self.__current_state = self.state

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        logger.info("saving the model")
        allowed_next = TRANSITIONS[self.__current_state]
        updated = self.state != self.__current_state

        if self.pk and updated and self.state not in allowed_next:
            raise Exception("Invalid transition",self.state,allowed_next)
        
        if self.pk and updated:
            self.__current_state = self.state

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
    
    def _transition(self,state):
        self.state = state
        self.save()

    def assign(self,driver):
        logger.info("assigning")
        self._transition(STATE_WAITING)

    def accept(self):
        logger.info("accepting")
        self._transition(STATE_TO_AIRPORT)
    
    def decline(self):
        logger.info("declining")
        self._transition(STATE_REQUEST)

    def picked_up(self):
        logger.info("picking up")
        self._transition(STATE_TO_HOTEL)

    def dropped_off(self):
        logger.info("dropping off!")
        self._transition(STATE_DROPPED_OFF)