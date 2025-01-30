import fitz  # PyMuPDF
import os
from faker import Faker
import random
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('form_filler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ADACBoatFormFiller:
    def __init__(self):
        self.faker = Faker('de_DE')

    def get_form_fields(self, pdf_path):
        """Get all form fields from the PDF"""
        doc = fitz.open(pdf_path)
        fields = []
        for page in doc:
            widgets = page.widgets()
            for widget in widgets:
                field_name = widget.field_name
                field_type = widget.field_type
                field_value = widget.field_value
                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'value': field_value
                })
                logger.debug(f"Found field: {field_name} (Type: {field_type})")
        doc.close()
        return fields

    def generate_form_data(self):
        """Generate random data for form fields"""
        price = random.randint(15000, 150000)
        
        return {
            'VKäufer_Name': self.faker.name(),
            'VKäufer_Straße': self.faker.street_address(),
            'VKäufer_PLZ': self.faker.postcode(),
            'VKäufer_Ort': self.faker.city(),
            'VKäufer Gebdatum': self.faker.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),
            'VKäufer_Tel': self.faker.phone_number(),
            
            'Käufer_Name': self.faker.name(),
            'Käufer_Straße': self.faker.street_address(),
            'Käufer_PLZ': self.faker.postcode(),
            'Käufer_Ort': self.faker.city(),
            'Käufer Gebdatum': self.faker.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),
            'Käufer_Tel': self.faker.phone_number(),
            
            'Werft': random.choice(['Bavaria Yachtbau', 'Dehler', 'Hanse Yachts']),
            'Boot_Modell': f"Sport {random.randint(28, 50)}",
            'Bootsname': self.faker.first_name(),
            'LüA': f"{random.uniform(5.0, 15.0):.2f}",
            'BüA': f"{random.uniform(2.0, 4.5):.2f}",
            'Boot_Baujahr': str(random.randint(2010, 2023)),
            'WIN': f"DEX{random.randint(10000, 99999)}",
            
            'Motor': random.choice(['Volvo Penta', 'Mercury Marine', 'Yamaha Marine']),
            'Motor_Leistung': f"{random.randint(20, 300)} PS",
            'B_Stunden': str(random.randint(100, 2000)),
            'MotNr': f"ENG{random.randint(10000, 99999)}",
            
            'Kaufpreis': f"{price:,} €",
            'Kaufpreis_Worte': f"{price} Euro",
            
            'OrtDatum': f"{self.faker.city()}, {datetime.now().strftime('%d.%m.%Y')}",
        }

    def fill_form(self, template_path, output_path):
        """Fill a single PDF form"""
        try:
            # Open the PDF
            doc = fitz.open(template_path)
            
            # Generate random data
            form_data = self.generate_form_data()
            
            # Fill each field
            for page in doc:
                widgets = page.widgets()
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name in form_data:
                        widget.field_value = form_data[field_name]
                        widget.update()
                        logger.debug(f"Filled field {field_name} with value: {form_data[field_name]}")
            
            # Save the filled form
            doc.save(output_path)
            doc.close()
            
            logger.info(f"Successfully created: {output_path}")
            
        except Exception as e:
            logger.error(f"Error filling form: {str(e)}", exc_info=True)
            raise

    def generate_batch(self, template_path, output_dir, count):
        """Generate multiple filled forms"""
        logger.info(f"Starting batch generation of {count} forms")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # First, get and display all form fields
        logger.info("Analyzing form fields...")
        fields = self.get_form_fields(template_path)
        logger.info(f"Found {len(fields)} form fields:")
        for field in fields:
            logger.info(f"  {field['name']} ({field['type']})")
        
        for i in range(count):
            output_path = os.path.join(output_dir, f'boat_contract_{i+1}.pdf')
            try:
                self.fill_form(template_path, output_path)
                if (i + 1) % 10 == 0:
                    logger.info(f'Generated {i + 1} forms')
            except Exception as e:
                logger.error(f"Error generating form {i+1}: {str(e)}")
                continue

def main():
    # Paths
    template_path = 'adac_template.pdf'
    output_dir = 'filled_forms'
    
    logger.info("Starting form generation process")
    
    # Create form filler
    filler = ADACBoatFormFiller()
    
    # Generate forms (starting with a small number for testing)
    filler.generate_batch(template_path, output_dir, 10)
    
    logger.info("Form generation completed!")

if __name__ == "__main__":
    main()