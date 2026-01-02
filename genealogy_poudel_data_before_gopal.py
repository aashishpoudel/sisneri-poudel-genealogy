"""This contains all the Person data of Sisneri Poudels"""
from genealogy_class import Person

gopal_32 = Person("Gopal", gender="Male", name_nep="गोपाल", birth_year="~1620", gen_number=32, comment="काठमाण्डौ उपत्यका आउने")
root_person = gopal_32
ram_bhadra_33 = Person("Ram Bhadra", gender="Male", name_nep="रामभद्र", comment="लुभू सिस्नेरीमा बस्ने")
govinda_34 = Person("Govinda", gender="Male", name_nep="गोविन्द", comment="ठूलाघरे पूर्वज")
bishwamvar_34 = Person("Bishwamvar", gender="Male", name_nep="विश्वम्भर", gen_number=34, comment="पुस्ता जोड्न नसकिएको तर प्रजापतिभन्दा यिनको नाम अगाडि देखिएकोले पुस्ता ३४ अनुमानित")
prajapati_34 = Person("Prajapati", gender="Male", name_nep="प्रजापति", birth_year=1650, comment="आँटीघरे पूर्वज\nसन् १६७७ मा श्रीनिवास मल्लबाट विर्ता")
chamu_34 = Person("Chamu", gender="Male", name_nep="चामु", comment="तीनघरेका पूर्वज")

gautam_35 = Person("Gautam", gender="Male", name_nep="गौतम", comment="जेठा पण्डित फेटका पूर्वज")
gangaram_35 = Person("Gangaram", gender="Male", name_nep="गंगाराम", place="लामाटार")
bhrigu_35 = Person("Bhrigu", gender="Male", name_nep="भृगु")

laxmidhar_36 = Person("Laxmidhar", gender="Male", name_nep="लक्ष्मीधर")
ramchandra_36 = Person("RamChandra", gender="Male", name_nep="रामचन्द्र")
devhari_kancha_36 = Person("DevHari", gender="Male", name_nep="देवहरि")

laxminarayan_37 = Person("LaxmiNarayan", gender="Male", name_nep="लक्ष्मीनारायण")
vidya_nanda_38 = Person("VidyaNanda", gender="Male", name_nep="विद्यानन्द")
dharma_nanda_39 = Person("DharmaNanda", gender="Male", name_nep="धर्मानन्द")
harilal_40 = Person("HariLal", gender="Male", name_nep="हरिलाल")
shiva_nidhi_41 = Person("ShivaNidhi", gender="Male", name_nep="शिवनिधि")
gedlal_42 = Person("GedLal", gender="Male", name_nep="गेदलाल")
lekhnath_42 = Person("LekhNath (Gopal)", gender="Male", name_nep="लेखनाथ(गोपाल)")
premnath_42 = Person("PremNath", gender="Male", name_nep="प्रेमनाथ")
ramchandra_36_2 = Person("RamChandra", gender="Male", name_nep="रामचन्द्र")
ratan_37 = Person("Ratan", gender="Male", name_nep="रतन")
nini_38 = Person("Nini", gender="Male", name_nep="नीनी")
vijayananda_39 = Person("VijayaNanda", gender="Male", name_nep="विजयानन्द")
gaurishankar_40 = Person("GauriShankar", gender="Male", name_nep="गौरीशंकर")

bali_35 = Person("Bali", gender="Male", name_nep="बलि")
parmananda_35 = Person("Parmananda", gender="Male", name_nep="परमानन्द", comment="कान्छा - दारिमपाटेका पुर्खा")
rambhadra_37 = Person("Rambhadra (Balbhadra)", gender="Male", name_nep="रामभद्र(बलभद्र)")


#### Add Children ####
#####################################################
gopal_32.add_children([ram_bhadra_33])
ram_bhadra_33.add_children([govinda_34, prajapati_34, chamu_34])
govinda_34.add_children([gautam_35, gangaram_35, bhrigu_35, bali_35, parmananda_35])
gautam_35.add_children([laxmidhar_36, ramchandra_36, devhari_kancha_36])
laxmidhar_36.add_children([laxminarayan_37, rambhadra_37])
ramchandra_36.add_children([ratan_37])
ratan_37.add_children([nini_38])
nini_38.add_children([vijayananda_39])
vijayananda_39.add_children([gaurishankar_40])

laxminarayan_37.add_children([vidya_nanda_38])
vidya_nanda_38.add_children([dharma_nanda_39])
dharma_nanda_39.add_children([harilal_40])
harilal_40.add_children([shiva_nidhi_41])



