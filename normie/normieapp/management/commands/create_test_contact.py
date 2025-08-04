from django.core.management.base import BaseCommand
from django.utils import timezone
from normieapp.models import ContactMessage

class Command(BaseCommand):
    help = 'Create test contact messages for inbox testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of test messages to create',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        test_messages = [
            {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'department': 'Engineering',
                'subject': 'norms',
                'message': 'Hello, I need help with understanding the new ISO standards for our project. Could you please provide guidance on the implementation requirements?',
                'status': 'new'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@company.com',
                'department': 'Quality Assurance',
                'subject': 'materials',
                'message': 'We need to test some new composite materials for aerospace applications. What is the process for material testing approval?',
                'status': 'in_progress'
            },
            {
                'name': 'Mike Chen',
                'email': 'mike.chen@supplier.com',
                'department': 'Supply Chain',
                'subject': 'chemicals',
                'message': 'I have questions about the chemical standards compliance for our new cleaning solvents. Please advise on the certification requirements.',
                'status': 'new'
            },
            {
                'name': 'Lisa Anderson',
                'email': 'lisa.anderson@rolls-royce.com',
                'department': 'Documentation',
                'subject': 'archival',
                'message': 'I need to access some archived specifications from 2019. Could you help me locate the documents for project RR-2019-045?',
                'status': 'resolved'
            },
            {
                'name': 'David Wilson',
                'email': 'david.wilson@contractor.com',
                'department': 'Manufacturing',
                'subject': 'specs',
                'message': 'There seems to be a discrepancy in the latest specification document. Section 4.2.1 conflicts with our previous understanding. Please clarify.',
                'status': 'new'
            }
        ]
        
        created_count = 0
        for i in range(count):
            # Cycle through test messages if count > len(test_messages)
            message_data = test_messages[i % len(test_messages)]
            
            # Modify name and email slightly for uniqueness
            if i >= len(test_messages):
                suffix = f" ({i + 1})"
                message_data = message_data.copy()
                message_data['name'] += suffix
                message_data['email'] = message_data['email'].replace('@', f'+{i}@')
            
            contact_message = ContactMessage.objects.create(**message_data)
            created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Created contact message {created_count}: {contact_message.name} - {contact_message.get_subject_display()}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} test contact messages')
        ) 