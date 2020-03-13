from autofixture import generators, register, AutoFixture
from .models import Detail, Job


class DetailAutoFixture(AutoFixture):
    field_values = {
        "original_machine": None,
        "ltd_item_number": generators.IntegerGenerator(min_value=1, max_value=50),
    }

    def pre_process_instance(self, instance):
        instance.outsource_detail_number = instance.ltd_item_number * 10

        return instance


class JobAutoFixture(AutoFixture):
    field_values = {
        "job_number": generators.IntegerGenerator(min_value=1000, max_value=9999)
    }


register(Detail, DetailAutoFixture)
register(Job, JobAutoFixture)
