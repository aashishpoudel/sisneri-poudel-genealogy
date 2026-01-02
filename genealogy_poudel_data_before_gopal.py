"""This contains all the Person data of Sisneri Poudels"""
from genealogy_class import Person

somnath_atreya_1 = Person("Shree Somnath Atreya", gender="Male", name_nep="श्री सोमनाथ आत्रेय", birth_year="463", gen_number=1)
first_person_listed = somnath_atreya_1
ranganav_2 = Person("Shree Ranganav", gender="Male", name_nep="श्री रङ्गनाभ")
tatwanav_2 = Person("Tatwanav", gender="Male", name_nep="तत्वनाभ")
puranav_3 = Person("Shree Puranav", gender="Male", name_nep="श्री पुरनाभ")
bhramanav_4 = Person("Shree Bhramanav", gender="Male", name_nep="श्री ब्रह्मनाभ")
fadindranav_4 = Person("Fadindranav", gender="Male", name_nep="फणिन्द्रनाभ")
kamalnav_4 = Person("Kamalanav", gender="Male", name_nep="कमलनाभ")

shankardev_5 = Person("ShankarDev", gender="Male", name_nep="शंकरदेव")
prasarnav_5 = Person("Prasarnav", gender="Male", name_nep="प्रसरनाभ")

bhimdev_6 = Person("BhimDev", gender="Male", name_nep="भिमदेव")
jayadev_6 = Person("JayaDev", gender="Male", name_nep="जयदेव")

purnadev_7 = Person("PurnaDev", gender="Male", name_nep="पुर्णदेव")
devdev_8 = Person("DevDev", gender="Male", name_nep="देवदेव")

kumardev_9 = Person("KumarDev", gender="Male", name_nep="कुमारदेव")
baldev_9 = Person("BalDev", gender="Male", name_nep="बलदेव")


shaktibhatta_10 = Person("BalDev", gender="Male", name_nep="शक्तिभट्ट")
nagdev_11 = Person("NagDev", gender="Male", name_nep="नागदेव")
prithvibhatta_11 = Person("BalDev", gender="Male", name_nep="पृथ्वीभट्ट")
shankar_bhattarak_11 = Person("BalDev", gender="Male", name_nep="शंकर भट्टारक")

kuberbhatta_12 = Person("KuberBhatta", gender="Male", name_nep="कुबेरभट्ट")
devendradev_12 = Person("DevendraDev", gender="Male", name_nep="देवेन्द्रदेव")

udayananda_bhatta_13 = Person("UdayaNandaBhatta", gender="Male", name_nep="उदयानन्दभट्ट")
sudayananda_bhatta_14 = Person("SudayaNandaBhatta", gender="Male", name_nep="सुदयानन्दभट्ट")
raya_bhatta_15 = Person("RayaBhatta", gender="Male", name_nep="रायभट्ट")
dev_dutta_16 = Person("DevDutta", gender="Male", name_nep="देवदत्त")

batsaraj_17 = Person("BatsaRaj", gender="Male", name_nep="वत्सराज")
upabatsaraj_18 = Person("UpabatsaRaj", gender="Male", name_nep="उपवत्सराज")
shreebatsaraj_19 = Person("ShreeBatsaraj", gender="Male", name_nep="श्री वत्सराज")
shreedev_20 = Person("ShreeDev", gender="Male", name_nep="श्रीदेव")

shreenanda_21 = Person("ShreeNanda", gender="Male", name_nep="श्रीनन्द")
shreeram_22 = Person("ShreeRam", gender="Male", name_nep="श्रीराम")
haridutta_23 = Person("HariDutta", gender="Male", name_nep="हरिदत्त")
krishnaram_24 = Person("KrishnaRam", gender="Male", name_nep="कृष्णराम")


chawa_25 = Person("Chawa", gender="Male", name_nep="चावा")
sawa_25 = Person("Sawa", gender="Male", name_nep="सावा")
narsingh_aryal_26 = Person("Narsingh Aryal", gender="Male", name_nep="नरसिंह अर्याल")
motiraj_26 = Person("MotiRaj", gender="Male", name_nep="मोतिराज")


####################################
somnath_atreya_1.add_children([ranganav_2, tatwanav_2])
ranganav_2.add_children([puranav_3])
puranav_3.add_children([bhramanav_4, fadindranav_4, kamalnav_4])
bhramanav_4.add_children([shankardev_5])
fadindranav_4.add_children([prasarnav_5])
prasarnav_5.add_children([bhimdev_6, jayadev_6])
bhimdev_6.add_children([purnadev_7])
purnadev_7.add_children([devdev_8])
devdev_8.add_children([kumardev_9, baldev_9])
kumardev_9.add_children([shaktibhatta_10])

shaktibhatta_10.add_children([nagdev_11, prithvibhatta_11, shankar_bhattarak_11])





####################################
gopal_32 = Person("Gopal", gender="Male", name_nep="गोपाल", birth_year="~1620", gen_number=32, comment="काठमाण्डौ उपत्यका आउने")
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



