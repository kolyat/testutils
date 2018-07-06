import random
import seleniumbase
import mimesis
import mimesis.builtins
from mimesis import enums

from tools import rndutils


def new_person():
    """Generate data for fake person

    :return: dict with person data
    """
    random.seed()
    _person = mimesis.Person(locale='ru')
    _person_ru = mimesis.builtins.RussiaSpecProvider()
    _date = mimesis.Datetime()
    _gender = random.choice((enums.Gender.MALE, enums.Gender.FEMALE))
    return {
        'first_name': _person.name(_gender),
        'last_name': _person.surname(_gender),
        'patr_name': _person_ru.patronymic(_gender),
        'license_series': rndutils.random_numstr(4),
        'license_number': rndutils.random_numstr(6),
        'start_date': _date.date(start=2000, end=2016, fmt='%d%m%Y'),
        'birth_date': _date.date(start=1950, end=1970, fmt='%d%m%Y'),
        'email': _person.email(),
        'phone': _person.telephone(mask='#'*10),
        'password': _person.password()
    }


class TestOsago(seleniumbase.BaseCase):
    def test_01_rsa(self):
        """1 - Driver check
        """
        person = new_person()
        self.open('http://megarussd.dev.b2bpolis.ru/#/calculator/osago/')
        self.send_keys('#id_driver_osago_last_name_0', person['last_name'])
        self.send_keys('#id_driver_osago_first_name_0', person['first_name'])
        self.send_keys('#id_driver_osago_patronymic_0', person['patr_name'])
        self.send_keys('#id_driver_license_series', person['license_series'])
        self.send_keys('#id_driver_license_number', person['license_number'])
        self.send_keys('#id_driving_experience_started_0',
                       person['start_date'])
        self.send_keys('#id_driver_birth_date_0', person['birth_date'])
        self.assert_text('Водитель не прошел проверку по базе РСА',
                         '.js-check-in-rsa_message ui message error')

    def test_02_registration(self):
        """2 - Registration
        """
        person = new_person()
        self.open('http://megarussd.dev.b2bpolis.ru/#/registration')
        self.click('#id_is_natural_person')
        self.send_keys('#id_last_name', person['last_name'])
        self.send_keys('#id_first_name', person['first_name'])
        self.send_keys('#id_patronymic', person['patr_name'])
        self.send_keys('#id_username_reg', person['email'])
        self.send_keys('#id_phone', person['phone'])
        self.send_keys('#id_password_reg', person['password'])
        self.send_keys('#id_password_repeat_reg', person['password'])
        self.click('[type="submit"]')
        self.assert_text(person['last_name'], '#id_last_name')
        self.assert_text(person['first_name'], '#id_first_name')
        self.assert_text(person['patr_name'], '#id_patronymic')


if __name__ == '__main__':
    import pytest
    pytest.main()
