import random

from list.models import Job, Detail


def create_jobs(num_jobs, customers):
    for x, i in enumerate(range(num_jobs)):
        rand_job_number = random.randrange(1000, 9999)
        rand_customer = random.choice(customers)
        rand_tools = random.choice([True, False])
        Job.objects.create(
            job_number=rand_job_number, customer=rand_customer, add_tools=rand_tools,
        )


def create_details(num_details, job, machine):
    for _, i in enumerate(range(num_details)):
        Detail.objects.create(
            job=job,
            machine=machine,
            ltd_item_number=i,
            outsource_detail_number=str(i * 10),
        )
