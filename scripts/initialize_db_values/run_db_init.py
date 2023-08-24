from config import default_log
from data.dbapi.company_management.company_read_queries import \
    find_companies_by_type
from data.dbapi.company_management.company_write_queries import add_new_company
from data.dbapi.company_management.dtos.add_company_dto import AddCompanyDTO
from data.enums.company_type import CompanyType
from scripts.initialize_db_values.add_roles_and_permissions import \
    create_roles_and_permissions


def create_entries():
    pass

if __name__ == '__main__':
    create_entries()
