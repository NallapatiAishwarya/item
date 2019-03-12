from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///universities.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete UniversityName if exisitng.
session.query(UniversityName).delete()
# Delete CollegeName if exisitng.
session.query(CollegeName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="Nallapati Aishwarya",
                 email="aishwarya.nallapati@gmail.com",
                 picture='http://www.enchanting-costarica.com/wp-content/'
                 'uploads/2018/02/jcarvaja17-min.jpg')
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample Universities
University1 = UniversityName(name="JNTUK",
                     user_id=1)
session.add(University1)
session.commit()

University2 = UniversityName(name="ACHARYA NAGARJUNA",
                     user_id=1)
session.add(University2)
session.commit

University3 = UniversityName(name="UNIVERSITY OF DELHI",
                     user_id=1)
session.add(University3)
session.commit()

University4 = UniversityName(name="ANNA UNIVERSITY",
                     user_id=1)
session.add(University4)
session.commit()

University5 = UniversityName(name="UNIVERSITY OF KOTA",
                     user_id=1)
session.add(University5)
session.commit()

University6 = UniversityName(name="UNIVERSITY OF MADRAS",
                     user_id=1)
session.add(University6)
session.commit()

# Populare a universities with colleges affiliated
# Using different users for colleges names year also
College1 = CollegeName(name="Narasaraopeta Engineering College",
                       establishedyear="1989",
                       rating="5",
                       universitynameid=1,
                       user_id=1)
session.add(College1)
session.commit()

College2 = CollegeName(name="Bapatla womens college",
                       establishedyear="1990",
                       rating="4",
                       universitynameid=2,
                       user_id=1)
session.add(College2)
session.commit()

College3 = CollegeName(name="College of Arts",
                       establishedyear="1988",
                       rating="5",
                       universitynameid=3,
                       user_id=1)
session.add(College3)
session.commit()

College4 = CollegeName(name="A.C.T College of Engineering and Technology",
                       establishedyear="1980",
                       rating="4",
                       universitynameid=4,
                       user_id=1)
session.add(College4)
session.commit()

College5 = CollegeName(name="Government Girls College,Baran",
                       establishedyear="1984",
                       rating="3",
                       universitynameid=5,
                       user_id=1)
session.add(College5)
session.commit()

College6 = CollegeName(name="Alpha Arts and Science College, Chennai",
                       establishedyear="1987",
                       rating="5",
                       universitynameid=6,
                       user_id=1)
session.add(College6)
session.commit()

print("Your universities database has been inserted successfully!")
