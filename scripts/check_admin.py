import sys
sys.path.insert(0, r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip')

from app import app, db, User

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(ra='admin').first()
    
    if admin:
        print(f"✓ Admin user exists")
        print(f"  RA: {admin.ra}")
        print(f"  Nome: {admin.nome}")
        print(f"  Is Admin: {admin.is_admin}")
        print(f"  Cargo: {admin.cargo}")
        
        # Test password
        if admin.check_password('admin123'):
            print("✓ Password 'admin123' is correct")
        else:
            print("✗ Password 'admin123' is INCORRECT")
            print("  Recreating admin user...")
            db.session.delete(admin)
            db.session.commit()
            
            # Create new admin
            new_admin = User(
                ra='admin',
                nome='Administrador',
                curso='Ciência da Computação',
                semestre=8,
                turma='A',
                numero_camisa=None,
                cargo='Admin',
                is_admin=True
            )
            new_admin.set_password('admin123')
            db.session.add(new_admin)
            db.session.commit()
            print("✓ Admin user recreated with password 'admin123'")
    else:
        print("✗ Admin user does NOT exist")
        print("  Creating admin user...")
        
        admin = User(
            ra='admin',
            nome='Administrador',
            curso='Ciência da Computação',
            semestre=8,
            turma='A',
            numero_camisa=None,
            cargo='Admin',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created with password 'admin123'")
    
    # List all users
    all_users = User.query.all()
    print(f"\nTotal users in database: {len(all_users)}")
    for user in all_users:
        print(f"  - RA: {user.ra}, Nome: {user.nome}, Admin: {user.is_admin}")
