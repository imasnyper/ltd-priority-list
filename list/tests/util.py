import random

from list.models import Job


def create_jobs(num_jobs, machine, customers):
    for x, i in enumerate(range(num_jobs)):
        rand_job_number = random.randrange(1000, 9999)
        rand_customer = random.choice(customers)
        rand_tools = random.choice([True, False])
        Job.objects.create(
            job_number=rand_job_number,
            machine=machine,
            customer=rand_customer,
            add_tools=rand_tools,
            description=f"{machine.name} job {i}"
        )