import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clinic.models import Doenca, Sintoma

doencas = [
    {
        'nome': 'Gastrite',
        'descricao': 'Inflamação da mucosa gástrica',
        'sintomas': ['Vômito', 'Dor Abdominal', 'Perda de Apetite', 'Letargia']
    },
    {
        'nome': 'Gripe Canina',
        'descricao': 'Infecção respiratória viral',
        'sintomas': ['Tosse', 'Secreção Nasal', 'Febre', 'Letargia', 'Perda de Apetite']
    },
    {
        'nome': 'Parvovirose Canina',
        'descricao': 'Doença viral altamente contagiosa que afeta principalmente filhotes',
        'sintomas': ['Diarreia', 'Vômito', 'Febre', 'Letargia', 'Perda de Apetite', 'Desidratação', 'Sangue nas Fezes']
    },
    {
        'nome': 'Cinomose',
        'descricao': 'Doença viral grave que afeta o sistema respiratório, digestivo e nervoso',
        'sintomas': ['Febre', 'Tosse', 'Secreção Nasal', 'Secreção Ocular', 'Vômito', 'Diarreia', 'Letargia', 'Convulsões', 'Tremores']
    },
    {
        'nome': 'Insuficiência Renal',
        'descricao': 'Falência progressiva da função renal',
        'sintomas': ['Aumento da Sede', 'Urinação Frequente', 'Perda de Apetite', 'Vômito', 'Letargia', 'Perda de Peso', 'Desidratação']
    },
    {
        'nome': 'Diabetes Mellitus',
        'descricao': 'Distúrbio metabólico caracterizado por hiperglicemia',
        'sintomas': ['Aumento da Sede', 'Urinação Frequente', 'Perda de Peso', 'Perda de Apetite', 'Letargia']
    },
    {
        'nome': 'Otite',
        'descricao': 'Inflamação do ouvido, comum em cães de orelhas caídas',
        'sintomas': ['Coceira', 'Secreção Ocular', 'Inchaço']
    },
    {
        'nome': 'Dermatite Alérgica',
        'descricao': 'Reação alérgica que afeta a pele',
        'sintomas': ['Coceira', 'Feridas na Pele', 'Inchaço']
    },
    {
        'nome': 'Pneumonia',
        'descricao': 'Infecção ou inflamação dos pulmões',
        'sintomas': ['Tosse', 'Dificuldade Respiratória', 'Febre', 'Letargia', 'Perda de Apetite', 'Secreção Nasal']
    },
    {
        'nome': 'Pancreatite',
        'descricao': 'Inflamação do pâncreas',
        'sintomas': ['Dor Abdominal', 'Vômito', 'Diarreia', 'Perda de Apetite', 'Letargia', 'Febre']
    },
    {
        'nome': 'Giardíase',
        'descricao': 'Infecção intestinal causada por protozoário',
        'sintomas': ['Diarreia', 'Perda de Peso', 'Perda de Apetite', 'Vômito']
    },
    {
        'nome': 'Cistite',
        'descricao': 'Inflamação da bexiga',
        'sintomas': ['Urinação Frequente', 'Sangue na Urina', 'Dor Abdominal', 'Letargia']
    },
    {
        'nome': 'Epilepsia',
        'descricao': 'Distúrbio neurológico caracterizado por convulsões recorrentes',
        'sintomas': ['Convulsões', 'Tremores']
    },
    {
        'nome': 'Obesidade',
        'descricao': 'Acúmulo excessivo de gordura corporal',
        'sintomas': ['Ganho de Peso Excessivo', 'Dificuldade Respiratória', 'Letargia', 'Claudicação']
    },
    {
        'nome': 'Artrite',
        'descricao': 'Inflamação das articulações',
        'sintomas': ['Claudicação', 'Letargia', 'Inchaço']
    },
    {
        'nome': 'Doença do Carrapato',
        'descricao': 'Doenças transmitidas por carrapatos como erliquiose e babesiose',
        'sintomas': ['Febre', 'Letargia', 'Perda de Apetite', 'Apatia', 'Sangue na Urina']
    },
    {
        'nome': 'Traqueobronquite Infecciosa',
        'descricao': 'Conhecida como tosse dos canis, altamente contagiosa',
        'sintomas': ['Tosse', 'Secreção Nasal', 'Febre', 'Letargia']
    }
]

criadas = 0
for doenca_data in doencas:
    doenca, created = Doenca.objects.get_or_create(
        nome=doenca_data['nome'],
        defaults={'descricao': doenca_data['descricao']}
    )
    
    if created:
        for sintoma_nome in doenca_data['sintomas']:
            try:
                sintoma = Sintoma.objects.get(nome=sintoma_nome)
                doenca.sintomas_associados.add(sintoma)
            except Sintoma.DoesNotExist:
                print(f'⚠️ Sintoma não encontrado: {sintoma_nome}')
        
        criadas += 1
        print(f'✓ {doenca.nome}')

print(f'\n{criadas} doenças adicionadas!')
print(f'Total: {Doenca.objects.count()} doenças cadastradas')
