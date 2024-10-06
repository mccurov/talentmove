import openai

openai.api_key = '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'

def enhance_job_description(job):
    prompt = f"""
    Улучши следующее описание вакансии, сделав его более привлекательным и информативным:

    Название: {job['title']}
    Компания: {job['company']}
    Описание: {job['description']}

    Улучшенное описание должно включать:
    1. Четкое описание обязанностей
    2. Ключевые требования к кандидату
    3. Преимущества работы в компании
    4. Возможности для роста и развития
    """

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    enhanced_description = response.choices[0].text.strip()
    job['enhanced_description'] = enhanced_description
    return job

def generate_catchy_title(job):
    prompt = f"""
    Создай привлекательный заголовок для следующей вакансии:

    Название: {job['title']}
    Компания: {job['company']}
    Описание: {job['description']}

    Заголовок должен быть кратким, информативным и привлекать внимание потенциальных кандидатов.
    """

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )

    catchy_title = response.choices[0].text.strip()
    job['catchy_title'] = catchy_title
    return job

# Пример использования
if __name__ == "__main__":
    job = {
        'title': 'Python Developer',
        'company': 'Tech Corp',
        'description': 'We are looking for a Python developer with 3+ years of experience.'
    }
    enhanced_job = enhance_job_description(job)
    enhanced_job = generate_catchy_title(enhanced_job)
    print(enhanced_job)