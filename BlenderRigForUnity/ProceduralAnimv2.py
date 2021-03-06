import bpy 
import mathutils as m
import math 
import pickle


def matrix_to_euler(mat): 

	quat = mat.to_quaternion()
	eul = quat.to_euler()
	eul = [math.degrees(e) for e in eul]
	return eul

def matrix_to_list(mat): 
	
	to_vec = list(mat)
	to_tuple = [v.to_tuple() for v in to_vec]
	return to_tuple

def list_to_matrix(liste): 

	return m.Matrix(liste)

def add_frames(nb_frames): 

	current = bpy.context.scene.frame_current
	bpy.context.scene.frame_current = current + nb_frames

def set_frame(nb_frames): 

	bpy.context.scene.frame_current = nb_frames



class Skeleton(): 

	def __init__(self, armature, load = False, path = ''): 

		self.armature = armature
		self.footL = self.armature.data.bones['Foot Control L']
		self.footR = self.armature.data.bones['Foot Control R']
		self.handL = self.armature.data.bones['IK Arm L']
		self.handR = self.armature.data.bones['IK Arm R']
		self.head = self.armature.data.bones['Head']
		self.pelvis = self.armature.data.bones['Pelvis']
		self.spine1 = self.armature.data.bones['Spine1']
		self.spine2 = self.armature.data.bones['Spine2']

		self.legL = self.armature.data.bones['Leg L']
		self.legR = self.armature.data.bones['Leg R']

		self.shouL = self.armature.data.bones['Upperarm L']
		self.shouR = self.armature.data.bones['Upperarm R']

		self.targetArmL = self.armature.data.bones['IKT Arm L']
		self.targetArmR = self.armature.data.bones['IKT Arm R']

		self.targetLegL = self.armature.data.bones['IKT Leg L']
		self.targetLegR = self.armature.data.bones['IKT Leg R']

		self.dico = {
		'footL':self.footL,
		'footR':self.footR,
		'armL':self.handL, 
		'armR':self.handR, 
		'pelvis':self.pelvis, 
		'spine1':self.spine1, 
		'spine2':self.spine2, 
		'head':self.head, 
		'targetLL':self.targetLegL, 
		'targetLR':self.targetLegR,
		'targetAL':self.targetArmL, 
		'targetAR':self.targetArmR
		}

		self.leg_length = self.legL.head_local.z - self.footL.head_local.z
		self.arm_length = self.handR.head_local.x - self.shouR.head_local.x

		self.get_inital_pose(path, load) # Getting bone.head_local gets the bone position in edit mode !! 

	def get_inital_pose(self, path, load): 


		self.initial_pose = {}

		if load: 

			pickled_pose = pickle.load(open(path, 'rb'))
			for entry in self.dico: 
				self.initial_pose[entry] = m.Matrix(pickled_pose[entry])
		else: 
			# In order to get the pose (matrix), make sure to have the bone as ACTIVE (selected isn't enough)
			self.reset_all()
			to_be_pickled = {}
			for bone in self.dico: 

				bpy.ops.pose.select_all(action = 'DESELECT')
				self.dico[bone].select = True
				self.armature.data.bones.active = self.dico[bone]
				pose = bpy.context.active_pose_bone.matrix
				pose_pickable = matrix_to_list(pose)
				self.initial_pose[bone] = pose
				to_be_pickled[bone] = pose_pickable


			pickle.dump(to_be_pickled, open(path, 'wb'))

	
		
	def reset_all(self):

		bpy.ops.pose.select_all(action = 'SELECT')
		bpy.ops.pose.loc_clear()
		bpy.ops.pose.rot_clear() 

	def confirm_animation_pose(self): 

		bpy.ops.pose.select_all(action = 'SELECT')
		bpy.ops.anim.keyframe_insert_menu(type = '__ACTIVE__', confirm_success = True)
		self.reset_all()

	def get_bone_rotation(self, entry): 

		self.set_active(entry)
		return bpy.context.active_pose_bone.matrix.to_quaternion()
		# return self.armature.pose.bones[entry].matrix.to_quaternion()

	def set_active(self, entry): 

		bpy.ops.pose.select_all(action = 'DESELECT')
		self.armature.data.bones.active = self.dico[entry]

	def move(self, name, vector): 

		if name in ['footL', 'footR']: 
			vector *= self.leg_length
		if name in ['armL', 'armR', 'targetLL', 'targetLR', 'targetAL', 'targetAR']:
			vector *= self.arm_length
		if name == 'pelvis': 
			vector *= self.leg_length

		self.set_active(name)
		bpy.ops.transform.translate(value = vector)

	def rotate(self, name, quaternion): 

		self.set_active(name)
		bpy.ops.transform.rotate(value = quaternion.angle, axis = quaternion.axis)

	def RunMale(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'Run')
		self.reset_all()
		set_frame(1)

		
		self.move('footL', m.Vector((0.0,0.6468410491943359,0.32542940974235535)))
		self.rotate('footL', m.Quaternion((0.8095934391021729,0.5869910717010498,1.0933560723458413e-09,0.0)))
		self.move('footR', m.Vector((0.0,-0.15668821334838867,0.37364116311073303)))
		self.rotate('footR', m.Quaternion((0.9968357682228088,0.07948871701955795,1.4805927317507184e-10,0.0)))
		self.move('armL', m.Vector((0.44656145572662354,0.8304474949836731,0.783440887928009)))
		self.move('armR', m.Vector((-0.4655771255493164,0.21218188107013702,0.07616782188415527)))
		self.rotate('pelvis', m.Quaternion((0.9693430066108704,0.24575096368789673,0.0,-4.5774670165421583e-10)))
		self.rotate('spine1', m.Quaternion((0.9893530011177063,0.11518877744674683,0.047148920595645905,-0.07542866468429565)))
		self.rotate('spine2', m.Quaternion((0.9884982109069824,0.0800093486905098,0.08261135220527649,-0.09820865094661713)))
		self.move('targetAL', m.Vector((0.7912756204605103,1.1956740617752075,0.76777184009552)))
		self.move('targetAR', m.Vector((-0.0,-0.0,1.172295093536377)))


		self.confirm_animation_pose()
		add_frames(10)


		self.move('footL', m.Vector((0.0,0.8242871761322021,0.7037578225135803)))
		self.rotate('footL', m.Quaternion((0.8095934391021729,0.5869910717010498,1.0933560723458413e-09,0.0)))
		self.move('footR', m.Vector((0.0,-0.5718450546264648,0.16606272757053375)))
		self.rotate('footR', m.Quaternion((0.9527202844619751,-0.3038487732410431,0.0,0.0)))
		self.move('armL', m.Vector((0.827400803565979,1.3146575689315796,0.930336058139801)))
		self.move('armR', m.Vector((-0.6877334117889404,0.0870489701628685,0.41257596015930176)))
		self.rotate('pelvis', m.Quaternion((0.9693430066108704,0.24575096368789673,0.0,-4.5774670165421583e-10)))
		self.rotate('spine1', m.Quaternion((0.9904395341873169,0.06155836582183838,0.06543537974357605,-0.10468326508998871)))
		self.rotate('spine2', m.Quaternion((0.9805094003677368,0.08000271022319794,0.09998319298028946,-0.1490096002817154)))
		self.move('targetAL', m.Vector((0.7912756204605103,1.1956740617752075,0.76777184009552)))
		self.move('targetAR', m.Vector((-0.0,-0.0,1.172295093536377)))


		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((-1.3754917915775877e-07,0.35181185603141785,0.7230424880981445)))
		self.rotate('footL', m.Quaternion((-0.6485740542411804,-0.7611515522003174,-1.0626004520730703e-09,0.0)))
		self.move('footR', m.Vector((0.0,0.07901378720998764,0.16606272757053375)))
		self.move('armL', m.Vector((0.7725597620010376,0.5312165021896362,1.055686593055725)))
		self.move('armR', m.Vector((-0.8365870118141174,0.47093522548675537,0.7572900056838989)))
		self.move('pelvis', m.Vector((-1.212404932005029e-08,0.004821172449737787,-0.05303293839097023)))
		self.rotate('pelvis', m.Quaternion((0.9693430066108704,0.24575096368789673,0.0,-4.5774670165421583e-10)))
		self.rotate('spine1', m.Quaternion((0.9856981635093689,0.1685202419757843,0.0,-5.551115123125783e-17)))
		self.rotate('spine2', m.Quaternion((0.9969902634620667,0.0775270164012909,-2.7755575615628914e-17,1.1102230246251565e-16)))
		self.move('targetAL', m.Vector((0.7912756204605103,1.1956740617752075,0.76777184009552)))
		self.move('targetAR', m.Vector((-0.0,-0.0,1.172295093536377)))

		self.confirm_animation_pose()

	def IdleCombat(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'IdleCombat')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.21914754807949066,0.4426664113998413,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511075615882874,0.0,0.0,-0.30885985493659973)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.11457973718643188,0.0)))
		self.move('armL', m.Vector((0.7801657915115356,-0.42323073744773865,1.1484779119491577)))
		self.move('armR', m.Vector((-1.1379348039627075,0.2638631761074066,1.2705512046813965)))
		self.move('pelvis', m.Vector((-3.717063881911669e-18,0.11718139052391052,-0.23101471364498138)))
		self.rotate('pelvis', m.Quaternion((0.997765302658081,-0.06696155667304993,2.3807040783196953e-09,2.248355945866365e-10)))
		self.rotate('spine1', m.Quaternion((0.9869847893714905,0.16081368923187256,4.4861780956750863e-10,-2.3539430404895256e-09)))
		self.rotate('spine2', m.Quaternion((0.9873967170715332,0.1582651138305664,4.415078858066579e-10,-2.3166366602822563e-09)))
		self.rotate('head', m.Quaternion((0.9878208041191101,-0.1555955410003662,-6.012639275354559e-10,-3.18025139556255e-09)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.1125181913375854,-0.36474359035491943,-0.0)))
		self.move('targetAR', m.Vector((-2.8919358253479004,1.0182238817214966,-0.0)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.21914754807949066,0.4426664113998413,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511075615882874,0.0,0.0,-0.30885985493659973)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.11457973718643188,0.0)))
		self.move('armL', m.Vector((0.7801657915115356,-0.4341118633747101,1.0451072454452515)))
		self.move('armR', m.Vector((-1.1379348039627075,0.2529820501804352,1.363040804862976)))
		self.move('pelvis', m.Vector((-7.434134381268239e-18,0.13726963102817535,-0.24775491654872894)))
		self.rotate('pelvis', m.Quaternion((0.9984706044197083,-0.05546087026596069,2.3779556101999333e-09,2.522512199121252e-10)))
		self.rotate('spine1', m.Quaternion((0.9869848489761353,0.16081368923187256,5.027395166834481e-10,-2.3429809203889818e-09)))
		self.rotate('spine2', m.Quaternion((0.9804763793945312,0.19663673639297485,5.842855643756195e-10,-2.2848078984338827e-09)))
		self.rotate('head', m.Quaternion((0.9885472059249878,-0.15091297030448914,-2.621578509831579e-10,-3.2259568349957135e-09)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.1125181913375854,-0.36474359035491943,-0.0)))
		self.move('targetAR', m.Vector((-2.8919358253479004,1.0182238817214966,-0.0)))

		self.confirm_animation_pose()

	def HitUppercut(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'Uppercut')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.21914756298065186,0.4426664412021637,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511076211929321,0.0,0.0,-0.3088598847389221)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.11457973718643188,0.0)))
		self.move('armL', m.Vector((0.7801657915115356,-0.42323073744773865,1.1484779119491577)))
		self.move('armR', m.Vector((-1.1379348039627075,0.2638631761074066,1.2705512046813965)))
		self.move('pelvis', m.Vector((-3.717063881911669e-18,0.11718139797449112,-0.23101471364498138)))
		self.rotate('pelvis', m.Quaternion((0.9977654218673706,-0.06696084141731262,2.2483326311828478e-10,-2.3806798754577585e-09)))
		self.rotate('spine1', m.Quaternion((0.9869847297668457,0.16081371903419495,4.4861692138908893e-10,-2.3539425964003158e-09)))
		self.rotate('spine2', m.Quaternion((0.9873965978622437,0.15826478600502014,4.4150705313938943e-10,-2.316631331211738e-09)))
		self.rotate('head', m.Quaternion((0.9878209829330444,-0.15559512376785278,-6.012628173124313e-10,-3.1802411815107234e-09)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.1125181913375854,-0.36474359035491943,-0.0)))
		self.move('targetAR', m.Vector((-2.8919358253479004,1.0182238817214966,-0.0)))



		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.21914757788181305,0.4426664710044861,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511077404022217,0.0,0.0,-0.3088594973087311)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.296706885099411,0.0)))
		self.move('armL', m.Vector((0.8935108184814453,0.613247275352478,1.2770617008209229)))
		self.move('armR', m.Vector((-0.7297666072845459,-0.4305644631385803,1.0774867534637451)))
		self.move('pelvis', m.Vector((0.08292598277330399,0.11718141287565231,-0.3189782500267029)))
		self.rotate('pelvis', m.Quaternion((0.9918255805969238,-0.06656268239021301,0.007295642048120499,-0.10870914161205292)))
		self.rotate('spine1', m.Quaternion((0.9869809150695801,0.15637899935245514,-7.817521691322327e-05,0.03760858625173569)))
		self.rotate('spine2', m.Quaternion((0.8314930200576782,0.30407586693763733,0.14918692409992218,-0.44034144282341003)))
		self.rotate('head', m.Quaternion((0.9878208637237549,-0.08625863492488861,0.11863088607788086,0.05192394554615021)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.1125181913375854,-0.36474359035491943,1.0242846012115479)))
		self.move('targetAR', m.Vector((0.33159828186035156,1.0182238817214966,-0.0)))



		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.21914757788181305,0.5147422552108765,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511077404022217,0.0,0.0,-0.3088594973087311)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.30503979325294495,0.0)))
		self.move('armL', m.Vector((0.7044332027435303,0.03140902519226074,0.9562919735908508)))
		self.move('armR', m.Vector((-1.3558244705200195,0.9278703331947327,1.3841233253479004)))
		self.move('pelvis', m.Vector((0.11315133422613144,-0.07114581018686295,-0.3515286147594452)))
		self.rotate('pelvis', m.Quaternion((0.9960921406745911,0.07039684057235718,0.010872609913349152,-0.052402615547180176)))
		self.rotate('spine1', m.Quaternion((0.9693575501441956,0.034879058599472046,-0.0490303710103035,0.23817075788974762)))
		self.rotate('spine2', m.Quaternion((0.9576491117477417,0.2825251519680023,-0.04307006299495697,0.03510802984237671)))
		self.rotate('head', m.Quaternion((0.9878209829330444,-0.12834756076335907,-0.04279458522796631,-0.07684636116027832)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((0.2428983449935913,-0.36474359035491943,1.0242846012115479)))
		self.move('targetAR', m.Vector((-1.7931771278381348,1.0182238817214966,0.21310532093048096)))



		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.21914757788181305,0.32993045449256897,0.0)))
		self.rotate('footL', m.Quaternion((-0.9511077404022217,0.0,0.0,-0.3088594973087311)))
		self.move('footR', m.Vector((-0.1480371057987213,-0.30503979325294495,0.0)))
		self.move('armL', m.Vector((0.7958346605300903,-0.4974138140678406,0.7473743557929993)))
		self.move('armR', m.Vector((-1.4994553327560425,1.344617486000061,0.1578199863433838)))
		self.move('pelvis', m.Vector((0.11315134167671204,-0.09123404324054718,-0.26314035058021545)))
		self.rotate('pelvis', m.Quaternion((0.9751129150390625,-0.027260690927505493,0.0011711642146110535,-0.2200678586959839)))
		self.rotate('spine1', m.Quaternion((0.9504943490028381,0.06152735650539398,0.00964134931564331,0.30443722009658813)))
		self.rotate('spine2', m.Quaternion((0.9609696269035339,0.0780058428645134,-0.04139180853962898,0.26218199729919434)))
		self.move('targetLL', m.Vector((-0.8584177494049072,-0.0,-0.0)))
		self.move('targetAL', m.Vector((0.2428983449935913,-0.36474359035491943,1.0242846012115479)))
		self.move('targetAR', m.Vector((-1.3990931510925293,-1.183652639389038,0.05249989032745361)))

		self.confirm_animation_pose()

	def NierDirect(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'NierDirect')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.026460731402039528,0.3897853493690491,0.0)))
		self.rotate('footL', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.34612053632736206)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.09174277633428574,0.0)))
		self.rotate('footR', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.34612053632736206)))
		self.move('armL', m.Vector((0.8313078880310059,-0.39813607931137085,0.45944881439208984)))
		self.move('armR', m.Vector((-1.272024154663086,0.141320139169693,1.120532512664795)))
		self.rotate('pelvis', m.Quaternion((0.9535099864006042,-0.07364386320114136,-0.022505372762680054,0.2913902699947357)))
		self.move('pelvis', m.Vector((1.742081146005603e-09,0.2313067764043808,-0.1147652417421341)))
		self.rotate('spine1', m.Quaternion((0.9895884394645691,0.1367088407278061,0.0007598252268508077,0.044998373836278915)))
		self.rotate('spine2', m.Quaternion((0.9847801923751831,0.018573010340332985,-0.012571381404995918,0.17235176265239716)))
		self.rotate('head', m.Quaternion((0.9698266983032227,-0.03957751393318176,-0.010363101959228516,-0.2403382956981659)))
		self.move('targetLL', m.Vector((-1.937756061553955,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.8775777816772461,-0.0,-0.0)))
		self.move('targetAR', m.Vector((-1.7722032070159912,-0.15358412265777588,-0.0)))



		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.026460731402039528,0.3897853493690491,0.0)))
		self.rotate('footL', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.34612053632736206)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.17749513685703278,0.0)))
		self.rotate('footR', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.34612053632736206)))
		self.move('armL', m.Vector((0.8313078880310059,-0.7017147541046143,0.39475154876708984)))
		self.move('armR', m.Vector((-1.272024154663086,0.713640570640564,0.4038877487182617)))
		self.rotate('pelvis', m.Quaternion((0.914976954460144,-0.0706678032875061,-0.03059367835521698,0.3961143493652344)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.3048088252544403,-0.14845366775989532)))
		self.rotate('spine1', m.Quaternion((0.9895884394645691,0.13466259837150574,0.030913203954696655,0.04031267762184143)))
		self.rotate('spine2', m.Quaternion((0.9847801327705383,0.026745636016130447,-0.007535816170275211,0.17156921327114105)))
		self.rotate('head', m.Quaternion((0.9698266983032227,-0.04451098293066025,-0.019706517457962036,-0.23888634145259857)))
		self.move('targetLL', m.Vector((-1.937756061553955,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.8775777816772461,-0.0,-0.0)))
		self.move('targetAR', m.Vector((-1.7722032070159912,-0.15358412265777588,-0.0)))



		self.confirm_animation_pose()
		add_frames(5)

		self.move('footL', m.Vector((0.026460731402039528,0.5926509499549866,0.0)))
		self.rotate('footL', m.Quaternion((-0.9844262599945068,0.0,0.0,-0.17579801380634308)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.16623049974441528,0.2866579294204712)))
		self.rotate('footR', m.Quaternion((0.9697246551513672,0.24420087039470673,5.422348578914143e-17,0.0)))
		self.move('armL', m.Vector((0.4912862777709961,-0.1091192364692688,-0.012456417083740234)))
		self.move('armR', m.Vector((-1.1962119340896606,0.6359500288963318,0.4038877487182617)))
		self.rotate('pelvis', m.Quaternion((0.9509943127632141,-0.04194921255111694,-0.02359294891357422,0.3054715692996979)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.23236986994743347,-0.16200341284275055)))
		self.rotate('spine1', m.Quaternion((0.9932671189308167,0.11442195624113083,0.007833302021026611,-0.0163295716047287)))
		self.rotate('spine2', m.Quaternion((0.9944694638252258,0.02750036120414734,-0.0007123053655959666,0.10135988146066666)))
		self.rotate('head', m.Quaternion((0.9920329451560974,-0.05601129308342934,-0.011701509356498718,-0.11223392188549042)))
		self.move('targetLL', m.Vector((-0.9688777923583984,-0.0,-0.0)))
		self.move('targetLR', m.Vector((0.1193469762802124,-0.0,-0.0)))
		self.move('targetAL', m.Vector((0.47158849239349365,-0.019041895866394043,0.3152146339416504)))
		self.move('targetAR', m.Vector((-1.5472300052642822,-0.15358412265777588,-0.0)))

		self.confirm_animation_pose()
		add_frames(10)
		
		self.move('footL', m.Vector((0.026460731402039528,0.3897853493690491,0.0)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.33096739649772644,0.0)))
		self.move('armL', m.Vector((1.2053508758544922,1.342653751373291,0.6341211795806885)))
		self.move('armR', m.Vector((-0.9581711292266846,0.3920111656188965,0.4038877487182617)))
		self.rotate('pelvis', m.Quaternion((0.9991284608840942,0.04197373986244202,-9.320019323924824e-18,-4.1359030627651384e-25)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.0049205380491912365,-0.1749144047498703)))
		self.rotate('spine1', m.Quaternion((0.9789032936096191,0.060621291399002075,0.028352320194244385,-0.1930534392595291)))
		self.rotate('spine2', m.Quaternion((0.990777850151062,0.04887975752353668,0.012846961617469788,-0.12571793794631958)))
		self.rotate('head', m.Quaternion((0.9543382525444031,-0.028724130243062973,-0.03360472992062569,0.29543912410736084)))
		self.move('targetAL', m.Vector((1.9523178339004517,-0.07883095741271973,1.3049498796463013)))
		self.move('targetAR', m.Vector((-0.8408421277999878,-0.15358412265777588,-0.0)))

		self.confirm_animation_pose()
		add_frames(5)

		self.move('footL', m.Vector((0.026460731402039528,0.38978537917137146,0.0)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.33096739649772644,0.0)))
		self.move('armL', m.Vector((1.409372091293335,1.4333298206329346,0.9605552554130554)))
		self.move('armR', m.Vector((-0.6948466897010803,0.18503844738006592,0.4038877487182617)))
		self.rotate('pelvis', m.Quaternion((0.9991283416748047,0.041974782943725586,9.320262515024915e-18,0.0)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.004920538514852524,-0.1749144047498703)))
		self.rotate('spine1', m.Quaternion((0.9459618330001831,0.10256257653236389,0.058694444596767426,-0.3019804358482361)))
		self.rotate('spine2', m.Quaternion((0.9866008162498474,0.10118603706359863,0.021224768832325935,-0.12621350586414337)))
		self.rotate('head', m.Quaternion((0.9543383121490479,-0.021487856283783913,-0.08822870999574661,0.28459179401397705)))
		self.move('targetAL', m.Vector((1.9523178339004517,-0.07883095741271973,1.3049498796463013)))
		self.move('targetAR', m.Vector((-0.8408421277999878,-0.15358412265777588,-0.0)))

		self.confirm_animation_pose()
		add_frames(5)

		self.move('footL', m.Vector((0.026460731402039528,0.38978537917137146,0.0)))
		self.rotate('footL', m.Quaternion((0.9999704957008362,0.0,0.0,0.007683478761464357)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.3256640136241913,0.0)))
		self.rotate('footR', m.Quaternion((0.9999704957008362,0.0,0.0,0.007683478761464357)))
		self.move('armL', m.Vector((1.3965569734573364,0.6092861890792847,1.362929344177246)))
		self.move('armR', m.Vector((-0.8944683074951172,0.1744149774312973,0.419775128364563)))
		self.rotate('pelvis', m.Quaternion((0.999210000038147,0.03945484757423401,0.0004994701594114304,0.006466934457421303)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.009939316660165787,-0.17358094453811646)))
		self.rotate('spine1', m.Quaternion((0.9480205178260803,0.10514932870864868,0.05545716732740402,-0.2951700985431671)))
		self.rotate('spine2', m.Quaternion((0.9875629544258118,0.10032735764980316,0.021571936085820198,-0.11911555379629135)))
		self.rotate('head', m.Quaternion((0.9575501084327698,-0.022929182276129723,-0.08230064809322357,0.2753158211708069)))
		self.move('targetLL', m.Vector((-0.04295828938484192,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.01945510506629944,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.909036636352539,-0.8704160451889038,1.2760202884674072)))
		self.move('targetAR', m.Vector((-1.3153762817382812,-1.119743824005127,-0.6874752044677734)))

		self.confirm_animation_pose()


	def NierPunch2(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'NierPunch2')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.026460731402039528,0.38978537917137146,0.0)))
		self.rotate('footL', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.3256640136241913,0.0)))
		self.rotate('footR', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('armL', m.Vector((1.3965569734573364,0.6092861890792847,1.362929344177246)))
		self.move('armR', m.Vector((-0.8944683074951172,0.1744149774312973,0.419775128364563)))
		self.rotate('pelvis', m.Quaternion((0.999210000038147,0.03945419192314148,-0.0004994615446776152,0.006466830149292946)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.009939316660165787,-0.17358094453811646)))
		self.rotate('spine1', m.Quaternion((0.9480205178260803,0.1051492691040039,0.05545714870095253,-0.2951698303222656)))
		self.rotate('spine2', m.Quaternion((0.9875630140304565,0.10032735019922256,0.021571936085820198,-0.11911549419164658)))
		self.rotate('head', m.Quaternion((0.957550048828125,-0.022929199039936066,-0.0823005735874176,0.2753155827522278)))
		self.move('targetLL', m.Vector((-0.04295828938484192,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.01945510506629944,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.909036636352539,-0.8704160451889038,1.2760202884674072)))
		self.move('targetAR', m.Vector((-1.3153762817382812,-1.119743824005127,-0.6874752044677734)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.026460731402039528,0.02010565623641014,0.0)))
		self.rotate('footL', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('footR', m.Vector((-0.2028655856847763,0.3439444899559021,0.0)))
		self.rotate('footR', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('armL', m.Vector((1.3965569734573364,0.8964272737503052,0.7357527017593384)))
		self.move('armR', m.Vector((-0.8944685459136963,-0.4036453366279602,0.6955817937850952)))
		self.rotate('pelvis', m.Quaternion((0.999210000038147,0.03945419192314148,-0.0004994615446776152,0.006466830149292946)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,0.009939316660165787,-0.17358094453811646)))
		self.rotate('spine1', m.Quaternion((0.9480205178260803,0.1051492691040039,0.05545714870095253,-0.2951698303222656)))
		self.rotate('spine2', m.Quaternion((0.9875630140304565,0.10032735019922256,0.021571936085820198,-0.11911549419164658)))
		self.rotate('head', m.Quaternion((0.957550048828125,-0.022929199039936066,-0.0823005735874176,0.2753155827522278)))
		self.move('targetLL', m.Vector((-0.04295828938484192,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.01945510506629944,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.909036636352539,-0.8704160451889038,0.2096344232559204)))
		self.move('targetAR', m.Vector((0.5893429517745972,1.849753737449646,-0.1547529697418213)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.13940982520580292,0.49103018641471863,0.0)))
		self.rotate('footL', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.3030877709388733,0.0)))
		self.rotate('footR', m.Quaternion((0.9999704957008362,0.0,0.0,0.007681648712605238)))
		self.move('armL', m.Vector((0.732105016708374,0.5903196334838867,0.39523398876190186)))
		self.move('armR', m.Vector((-1.4056435823440552,1.8954792022705078,0.7081252932548523)))
		self.rotate('pelvis', m.Quaternion((0.9608759880065918,0.13587114214897156,0.03302931785583496,0.23913338780403137)))
		self.move('pelvis', m.Vector((3.050342867183531e-09,-0.023808956146240234,-0.25554102659225464)))
		self.rotate('spine1', m.Quaternion((0.9676418304443359,0.10768729448318481,-0.03823191300034523,0.22496922314167023)))
		self.rotate('spine2', m.Quaternion((0.994856595993042,0.030212804675102234,0.08644275367259979,0.043304696679115295)))
		self.rotate('head', m.Quaternion((0.9575501680374146,0.027877483516931534,-0.16370999813079834,0.23562614619731903)))
		self.move('targetLL', m.Vector((-0.5549577474594116,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.01945510506629944,-0.0,-0.0)))
		self.move('targetAL', m.Vector((0.5554834604263306,-0.6455944776535034,-0.2745417356491089)))
		self.move('targetAR', m.Vector((-1.3153762817382812,-1.058175802230835,0.739041805267334)))

		self.confirm_animation_pose()

	def JumpingUppercut(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'JumpingUppercut')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.04736870154738426,0.14070932567119598,0.0)))
		self.rotate('footL', m.Quaternion((0.9653711915016174,0.0,0.0,-0.26088017225265503)))
		self.move('footR', m.Vector((-0.0412612147629261,0.6843134164810181,0.0)))
		self.rotate('footR', m.Quaternion((0.9656676650047302,0.0,0.0,-0.25978079438209534)))
		self.move('armL', m.Vector((1.264420509338379,0.788827121257782,1.0707449913024902)))
		self.move('armR', m.Vector((-0.6530870795249939,-0.7913079857826233,0.38291096687316895)))
		self.rotate('pelvis', m.Quaternion((0.9446955919265747,0.10463559627532959,-0.0342196524143219,-0.3089499771595001)))
		self.move('pelvis', m.Vector((5.6837759387917686e-08,0.29792240262031555,-0.23624075949192047)))
		self.rotate('spine1', m.Quaternion((0.9899641275405884,0.09734855592250824,0.032092828303575516,-0.09728499501943588)))
		self.rotate('spine2', m.Quaternion((0.9888162612915039,0.14913873374462128,-2.9802318834981634e-08,-2.9802318834981634e-08)))
		self.move('targetLL', m.Vector((0.7176127433776855,-0.0,-0.0)))
		self.move('targetLR', m.Vector((1.7777910232543945,-0.0,-0.0)))
		self.move('targetAL', m.Vector((1.2899198532104492,-0.0,1.7051241397857666)))
		self.move('targetAR', m.Vector((-1.2770533561706543,-0.15358209609985352,0.46764159202575684)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.19633689522743225,0.07976780086755753,0.0)))
		self.rotate('footL', m.Quaternion((0.9653711915016174,0.0,0.0,-0.26088017225265503)))
		self.move('footR', m.Vector((-0.0412612147629261,0.6843134164810181,0.0)))
		self.rotate('footR', m.Quaternion((0.9656676650047302,0.0,0.0,-0.25978079438209534)))
		self.move('armL', m.Vector((1.4349721670150757,0.8735527992248535,1.642918348312378)))
		self.move('armR', m.Vector((-0.6530870795249939,-0.23894065618515015,1.47664213180542)))
		self.rotate('pelvis', m.Quaternion((0.9357320070266724,0.16674557328224182,-0.05453190207481384,-0.30601856112480164)))
		self.move('pelvis', m.Vector((5.6837759387917686e-08,0.32839319109916687,-0.4163568615913391)))
		self.rotate('spine1', m.Quaternion((0.9759575724601746,0.1923864781856537,0.0533110648393631,-0.08747707307338715)))
		self.rotate('spine2', m.Quaternion((0.9678618311882019,0.25148266553878784,5.960464477539063e-08,-9.685754776000977e-08)))
		self.move('targetLL', m.Vector((0.7176127433776855,-0.0,-0.0)))
		self.move('targetLR', m.Vector((1.7777910232543945,-0.0,-0.0)))
		self.move('targetAL', m.Vector((2.503823757171631,0.4102674722671509,1.160459280014038)))
		self.move('targetAR', m.Vector((-1.2770533561706543,-0.15358209609985352,0.46764159202575684)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.1471882462501526,-0.05116933211684227,0.9018709063529968)))
		self.rotate('footL', m.Quaternion((0.9214747548103333,0.33646729588508606,-0.03977750614285469,-0.189978688955307)))
		self.move('footR', m.Vector((0.003429247997701168,0.47057825326919556,0.7057763934135437)))
		self.rotate('footR', m.Quaternion((0.925288200378418,0.3115732669830322,-0.02470671571791172,-0.2148338258266449)))
		self.move('armL', m.Vector((0.9116075038909912,0.5265388488769531,0.016602516174316406)))
		self.move('armR', m.Vector((-1.2227295637130737,0.6485849618911743,0.2830944061279297)))
		self.rotate('pelvis', m.Quaternion((0.9807338714599609,0.13421621918678284,-0.030563022941350937,-0.13868127763271332)))
		self.move('pelvis', m.Vector((5.6837759387917686e-08,0.16689807176589966,0.39843714237213135)))
		self.rotate('spine1', m.Quaternion((0.9825884699821472,0.1328316479921341,0.10294077545404434,-0.07923898845911026)))
		self.rotate('spine2', m.Quaternion((0.9741268157958984,0.21073748171329498,0.035211071372032166,0.07366686314344406)))
		self.move('targetLL', m.Vector((0.36936506628990173,-0.0,-1.260221004486084)))
		self.move('targetLR', m.Vector((1.2650715112686157,-0.0,-0.969732940196991)))
		self.move('targetAL', m.Vector((1.3907279968261719,0.20513403415679932,-0.6947665214538574)))
		self.move('targetAR', m.Vector((-1.0582624673843384,0.2387913465499878,-1.5688104629516602)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.07229077070951462,-0.14001575112342834,1.8037415742874146)))
		self.rotate('footL', m.Quaternion((0.7699038982391357,0.6336181163787842,-0.0749071016907692,-0.012843968346714973)))
		self.move('footR', m.Vector((0.048119693994522095,0.14656081795692444,1.4115524291992188)))
		self.rotate('footR', m.Quaternion((0.7998355627059937,0.5944996476173401,-0.047141753137111664,-0.06790384650230408)))
		self.move('armL', m.Vector((0.38824307918548584,0.17952507734298706,-1.6097126007080078)))
		self.move('armR', m.Vector((-1.142735242843628,1.313145399093628,-2.4818029403686523)))
		self.rotate('pelvis', m.Quaternion((0.9905625581741333,0.08063492178916931,0.008999459445476532,0.1105538010597229)))
		self.move('pelvis', m.Vector((5.6837759387917686e-08,0.005403041839599609,1.2132309675216675)))
		self.rotate('spine1', m.Quaternion((0.9899641275405884,0.056361932307481766,0.09543916583061218,-0.08766838908195496)))
		self.rotate('spine2', m.Quaternion((0.9777436852455139,0.13497664034366608,0.05427778884768486,0.1511705219745636)))
		self.move('targetLL', m.Vector((-0.2990950345993042,-0.0,-2.5204415321350098)))
		self.move('targetLR', m.Vector((0.41777920722961426,-0.0,-1.9394655227661133)))
		self.move('targetAL', m.Vector((0.18078386783599854,2.384185791015625e-07,-2.096104621887207)))
		self.move('targetAR', m.Vector((-0.8394718170166016,0.63116455078125,-3.60526180267334)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.030827853828668594,0.08393992483615875,0.6244503855705261)))
		self.rotate('footL', m.Quaternion((-0.905605673789978,-0.32853052020072937,0.050795771181583405,-0.26337406039237976)))
		self.move('footR', m.Vector((-0.10647774487733841,-0.02585485950112343,0.8248582482337952)))
		self.rotate('footR', m.Quaternion((-0.9349212646484375,-0.25857898592948914,0.023419560864567757,-0.24188977479934692)))
		self.move('armL', m.Vector((0.5276345610618591,0.24730996787548065,-0.7294430732727051)))
		self.move('armR', m.Vector((-0.9126734137535095,1.2272053956985474,-0.6311273574829102)))
		self.rotate('pelvis', m.Quaternion((0.9624034762382507,0.04955393075942993,0.04764736443758011,0.2628176510334015)))
		self.move('pelvis', m.Vector((2.290090428402891e-08,0.07990296930074692,0.5145849585533142)))
		self.rotate('spine1', m.Quaternion((0.9879552721977234,0.15387099981307983,0.011091142892837524,-0.012046679854393005)))
		self.rotate('spine2', m.Quaternion((0.9858719706535339,0.15792573988437653,-0.010994954966008663,0.0547269731760025)))
		self.rotate('head', m.Quaternion((0.9978999495506287,0.005426168441772461,-0.027516216039657593,-0.058387454599142075)))
		self.move('targetLL', m.Vector((-1.493059515953064,-0.0,-0.9679449200630188)))
		self.move('targetLR', m.Vector((-0.5730021595954895,-0.0,-0.7448281645774841)))
		self.move('targetAL', m.Vector((0.013592064380645752,-0.0,-0.17627358436584473)))
		self.move('targetAR', m.Vector((-1.413999080657959,0.14778900146484375,-1.3845570087432861)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.026460731402039528,0.38978537917137146,0.0)))
		self.rotate('footL', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.3461204469203949)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.09174277633428574,0.0)))
		self.rotate('footR', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.3461204469203949)))
		self.move('armL', m.Vector((0.6948672533035278,0.28957226872444153,0.29329872131347656)))
		self.move('armR', m.Vector((-0.8225029110908508,1.0458948612213135,1.1689471006393433)))
		self.rotate('pelvis', m.Quaternion((0.9552470445632935,0.045909881591796875,0.0586889311671257,0.2863047420978546)))
		self.move('pelvis', m.Vector((1.742081146005603e-09,0.12635190784931183,-0.17578329145908356)))
		self.rotate('spine1', m.Quaternion((0.9762630462646484,0.2118612825870514,-0.013718293979763985,0.042863067239522934)))
		self.rotate('spine2', m.Quaternion((0.9774634838104248,0.21110472083091736,-5.960465188081798e-08,8.195639367158947e-08)))
		self.rotate('head', m.Quaternion((0.994469940662384,0.018125420436263084,-0.02215203456580639,-0.10104598850011826)))
		self.move('targetLL', m.Vector((-1.937756061553955,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.8775777816772461,-0.0,-0.0)))
		self.move('targetAL', m.Vector((-0.0,-0.0,1.0206958055496216)))
		self.move('targetAR', m.Vector((-1.7722032070159912,-0.15358412265777588,-0.0)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.026460731402039528,0.38978537917137146,0.0)))
		self.rotate('footL', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.3461204469203949)))
		self.move('footR', m.Vector((-0.2028655856847763,-0.09174277633428574,0.0)))
		self.rotate('footR', m.Quaternion((-0.9381900429725647,0.0,0.0,-0.3461204469203949)))
		self.move('armL', m.Vector((0.8203052282333374,0.28957217931747437,0.9931105375289917)))
		self.move('armR', m.Vector((-1.2720240354537964,0.7520051002502441,1.670699119567871)))
		self.rotate('pelvis', m.Quaternion((0.9552470445632935,0.045909881591796875,0.0586889311671257,0.2863047420978546)))
		self.move('pelvis', m.Vector((1.742081146005603e-09,0.12635190784931183,-0.3951728045940399)))
		self.rotate('spine1', m.Quaternion((0.9762630462646484,0.2118612825870514,-0.013718293979763985,0.042863067239522934)))
		self.rotate('spine2', m.Quaternion((0.9774634838104248,0.21110472083091736,-5.960465188081798e-08,8.195639367158947e-08)))
		self.rotate('head', m.Quaternion((0.994469940662384,0.018125420436263084,-0.02215203456580639,-0.10104598850011826)))
		self.move('targetLL', m.Vector((-1.937756061553955,-0.0,-0.0)))
		self.move('targetLR', m.Vector((-0.8775777816772461,-0.0,-0.0)))
		self.move('targetAL', m.Vector((-0.0,-0.0,1.0206958055496216)))
		self.move('targetAR', m.Vector((-1.7722032070159912,-0.15358412265777588,-0.0)))

		self.confirm_animation_pose()

	def DashLateral(self): 

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'DashR')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.5222042798995972,-0.005565029103308916,-0.5110498070716858)))
		self.move('footR', m.Vector((-0.23781046271324158,0.1748749315738678,-0.5110498070716858)))
		self.move('armL', m.Vector((-0.02681732177734375,0.05738535523414612,-0.2712744176387787)))
		self.move('armR', m.Vector((0.441429078578949,0.05738523602485657,-0.19272282719612122)))
		self.rotate('pelvis', m.Quaternion((0.9932456612586975,-0.09341317415237427,0.06578686088323593,0.02070014737546444)))
		self.move('pelvis', m.Vector((-0.050784625113010406,0.0,-0.25915393233299255)))
		self.rotate('spine1', m.Quaternion((0.9807031154632568,0.19520102441310883,-0.004782840143889189,-0.009748213924467564)))
		self.rotate('spine2', m.Quaternion((0.9767711162567139,0.21227382123470306,0.021787129342556,0.01957916095852852)))
		self.move('targetLL', m.Vector((-0.39848193526268005,2.196868419647217,0.391836941242218)))
		self.move('targetLR', m.Vector((0.9249303936958313,0.6579889059066772,0.391836941242218)))
		self.move('targetAL', m.Vector((0.14018625020980835,-1.1920928955078125e-07,-0.6618927717208862)))
		self.move('targetAR', m.Vector((0.43748873472213745,-1.1920928955078125e-07,-1.1955543756484985)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.5222042798995972,-0.005565029103308916,-0.5110498070716858)))
		self.move('footR', m.Vector((-0.23781046271324158,0.1748749315738678,-0.5110498070716858)))
		self.move('armL', m.Vector((-0.02681732177734375,0.05738535523414612,-0.2712744176387787)))
		self.move('armR', m.Vector((0.419422447681427,0.623275637626648,0.4124605357646942)))
		self.rotate('pelvis', m.Quaternion((0.9932456612586975,-0.09341317415237427,0.06578686088323593,0.02070014737546444)))
		self.move('pelvis', m.Vector((-0.050784625113010406,0.0,-0.41827908158302307)))
		self.rotate('spine1', m.Quaternion((0.9807031154632568,0.19520102441310883,-0.004782840143889189,-0.009748213924467564)))
		self.rotate('spine2', m.Quaternion((0.9767711162567139,0.21227382123470306,0.021787129342556,0.01957916095852852)))
		self.move('targetLL', m.Vector((-0.39848193526268005,2.196868419647217,0.391836941242218)))
		self.move('targetLR', m.Vector((0.9249303936958313,0.6579889059066772,0.391836941242218)))
		self.move('targetAL', m.Vector((0.14018625020980835,-1.1920928955078125e-07,-0.6618927717208862)))
		self.move('targetAR', m.Vector((-0.640838086605072,-1.1920928955078125e-07,-0.3427961766719818)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.5946977734565735,-0.005565029103308916,-0.5071312189102173)))
		self.rotate('footL', m.Quaternion((0.8679088354110718,-9.252189014929968e-10,-0.4967235326766968,-7.031670890000896e-08)))
		self.move('footR', m.Vector((-0.05559714511036873,0.14774250984191895,-0.5110498070716858)))
		self.rotate('footR', m.Quaternion((0.9291046261787415,2.7553517245593184e-09,-0.36981725692749023,-4.684101284624376e-08)))
		self.move('armL', m.Vector((0.17694813013076782,0.05738532170653343,-0.016567617654800415)))
		self.move('armR', m.Vector((1.1586835384368896,0.05738520249724388,0.33706721663475037)))
		self.rotate('pelvis', m.Quaternion((0.978334903717041,-0.09521400928497314,0.18364542722702026,0.00942423939704895)))
		self.move('pelvis', m.Vector((-0.17617875337600708,2.1059754828911537e-08,-0.41589656472206116)))
		self.rotate('spine1', m.Quaternion((0.9807031750679016,0.1919664442539215,-0.004782848060131073,0.036706551909446716)))
		self.rotate('spine2', m.Quaternion((0.9767710566520691,0.20161691308021545,0.02178710140287876,0.06924034655094147)))
		self.move('targetLL', m.Vector((-0.39848193526268005,2.196868419647217,0.391836941242218)))
		self.move('targetLR', m.Vector((0.9249303936958313,0.6579889059066772,0.391836941242218)))
		self.move('targetAL', m.Vector((0.14018625020980835,-1.1920928955078125e-07,-0.6618927717208862)))
		self.move('targetAR', m.Vector((0.43748873472213745,-1.1920928955078125e-07,-1.1955543756484985)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.119,-0.006,-0.511)))
		self.move('footR', m.Vector((-0.641,0.175,-0.511)))
		self.move('armL', m.Vector((-0.027,0.057,-0.271)))
		self.move('armR', m.Vector((0.441,0.057,-0.193)))
		self.rotate('pelvis', m.Quaternion((0.994,-0.090,-0.052,0.032)))
		self.move('pelvis', m.Vector((-0.051,0.000,-0.259)))
		self.rotate('spine1', m.Quaternion((0.981,0.187,-0.005,-0.055)))
		self.rotate('spine2', m.Quaternion((0.977,0.211,0.022,-0.031)))
		self.move('targetLL', m.Vector((-0.398,2.197,0.392)))
		self.move('targetLR', m.Vector((0.925,0.658,0.392)))
		self.move('targetAL', m.Vector((0.140,-0.000,-0.662)))
		self.move('targetAR', m.Vector((0.437,-0.000,-1.196)))

		self.confirm_animation_pose()

		self.armature.animation_data_create()
		self.armature.animation_data.action = bpy.data.actions.new(name = 'DashL')
		self.reset_all()
		set_frame(1)

		self.move('footL', m.Vector((0.238,0.175,-0.511)))
		self.move('footR', m.Vector((-0.522,-0.006,-0.511)))
		self.move('armL', m.Vector((-0.441,0.057,-0.193)))
		self.move('armR', m.Vector((0.027,0.057,-0.271)))
		self.rotate('pelvis', m.Quaternion((0.993,-0.093,-0.066,-0.021)))
		self.move('pelvis', m.Vector((0.051,0.000,-0.259)))
		self.rotate('spine1', m.Quaternion((0.981,0.195,0.005,0.010)))
		self.rotate('spine2', m.Quaternion((0.977,0.212,-0.022,-0.020)))
		self.move('targetLL', m.Vector((-0.925,0.658,0.392)))
		self.move('targetLR', m.Vector((0.398,2.197,0.392)))
		self.move('targetAL', m.Vector((-0.437,-0.000,-1.196)))
		self.move('targetAR', m.Vector((-0.140,-0.000,-0.662)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.238,0.175,-0.511)))
		self.move('footR', m.Vector((-0.522,-0.006,-0.511)))
		self.move('armL', m.Vector((-0.419,0.623,0.412)))
		self.move('armR', m.Vector((0.027,0.057,-0.271)))
		self.rotate('pelvis', m.Quaternion((0.993,-0.093,-0.066,-0.021)))
		self.move('pelvis', m.Vector((0.051,0.000,-0.418)))
		self.rotate('spine1', m.Quaternion((0.981,0.195,0.005,0.010)))
		self.rotate('spine2', m.Quaternion((0.977,0.212,-0.022,-0.020)))
		self.move('targetLL', m.Vector((-0.925,0.658,0.392)))
		self.move('targetLR', m.Vector((0.398,2.197,0.392)))
		self.move('targetAL', m.Vector((0.641,-0.000,-0.343)))
		self.move('targetAR', m.Vector((-0.140,-0.000,-0.662)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.056,0.148,-0.511)))
		self.rotate('footL', m.Quaternion((0.929,0.000,0.370,0.000)))
		self.move('footR', m.Vector((-0.595,-0.006,-0.507)))
		self.rotate('footR', m.Quaternion((0.868,-0.000,0.497,0.000)))
		self.move('armL', m.Vector((-1.159,0.057,0.337)))
		self.move('armR', m.Vector((-0.177,0.057,-0.017)))
		self.rotate('pelvis', m.Quaternion((0.978,-0.095,-0.184,-0.009)))
		self.move('pelvis', m.Vector((0.176,0.000,-0.416)))
		self.rotate('spine1', m.Quaternion((0.981,0.192,0.005,-0.037)))
		self.rotate('spine2', m.Quaternion((0.977,0.202,-0.022,-0.069)))
		self.move('targetLL', m.Vector((-0.925,0.658,0.392)))
		self.move('targetLR', m.Vector((0.398,2.197,0.392)))
		self.move('targetAL', m.Vector((-0.437,-0.000,-1.196)))
		self.move('targetAR', m.Vector((-0.140,-0.000,-0.662)))

		self.confirm_animation_pose()
		add_frames(10)

		self.move('footL', m.Vector((0.641,0.175,-0.511)))
		self.move('footR', m.Vector((-0.119,-0.006,-0.511)))
		self.move('armL', m.Vector((-0.441,0.057,-0.193)))
		self.move('armR', m.Vector((0.027,0.057,-0.271)))
		self.rotate('pelvis', m.Quaternion((0.994,-0.090,0.052,-0.032)))
		self.move('pelvis', m.Vector((0.051,0.000,-0.259)))
		self.rotate('spine1', m.Quaternion((0.981,0.187,0.005,0.055)))
		self.rotate('spine2', m.Quaternion((0.977,0.211,-0.022,0.031)))
		self.move('targetLL', m.Vector((-0.925,0.658,0.392)))
		self.move('targetLR', m.Vector((0.398,2.197,0.392)))
		self.move('targetAL', m.Vector((-0.437,-0.000,-1.196)))
		self.move('targetAR', m.Vector((-0.140,-0.000,-0.662)))

		self.confirm_animation_pose()


	def print_pose(self): 

		for entry in self.dico: 
			initial = self.initial_pose[entry]

			self.armature.data.bones.active = self.dico[entry]
		

			current = bpy.context.active_pose_bone.matrix

			if entry in ['footL', 'footR']: 
				new_position = current.to_translation() 
				old_position = initial.to_translation()
				translation = new_position - old_position
				if translation.length > 0.001: 
					translation /= self.leg_length
					print('self.move(\'{}\', m.Vector(({:.3f},{:.3f},{:.3f})))'.format(entry, translation.x,translation.y,translation.z))
				
				new_rotation = current.to_quaternion()
				old_rotation = initial.to_quaternion()
				
				if new_rotation != old_rotation: 
					old_rotation.invert()
					rotation = new_rotation*old_rotation

					print('self.rotate(\'{}\', m.Quaternion(({:.3f},{:.3f},{:.3f},{:.3f})))'.format(entry, rotation.w,rotation.x,rotation.y,rotation.z))
				

			if entry in ['armL', 'armR', 'targetLL', 'targetLR', 'targetAL', 'targetAR']: 

				new_position = current.to_translation() 
				old_position = initial.to_translation()
				translation = new_position - old_position

				if translation.length > 0.001: 
					translation /= self.arm_length
					print('self.move(\'{}\', m.Vector(({:.3f},{:.3f},{:.3f})))'.format(entry, translation.x,translation.y,translation.z))


			if entry in ['head', 'spine1', 'spine2', 'pelvis']:


				if entry == 'pelvis':	

					old_rotation = m.Quaternion([0.7071,0.7071,0.,0.])

					new_rotation = self.get_bone_rotation('pelvis')

					if new_rotation != old_rotation: 
						# old_rotation.invert()
						rotation = old_rotation.rotation_difference(new_rotation)
						# rotation = (old_rotation*new_rotation).normalized()

						print('self.rotate(\'{}\', m.Quaternion(({:.3f},{:.3f},{:.3f},{:.3f})))'.format(entry, rotation.w,rotation.x,rotation.z,rotation.y))

					new_position = current.to_translation() 
					old_position = initial.to_translation()
					translation = new_position - old_position

					if translation.length > 0.05: 
						translation /= self.leg_length
						print('self.move(\'{}\', m.Vector(({:.3f},{:.3f},{:.3f})))'.format(entry, translation.x,translation.y,translation.z))
				
				else:
					if entry == 'spine1': 
						old_rotation = self.get_bone_rotation('pelvis')
						new_rotation = self.get_bone_rotation('spine1')
					elif entry == 'spine2': 
						old_rotation = self.get_bone_rotation('spine1')
						new_rotation = self.get_bone_rotation('spine2')
					elif entry == 'head': 
						old_rotation = self.get_bone_rotation('spine2')
						new_rotation = self.get_bone_rotation('head')

					if new_rotation != old_rotation: 

						c_o_r = old_rotation.copy()
						c_n_r = new_rotation.copy()
						c_o_r.invert()

						rotation = (c_n_r*c_o_r).normalized()
						print('self.rotate(\'{}\', m.Quaternion(({:.3f},{:.3f},{:.3f},{:.3f})))'.format(entry, rotation.w,rotation.x,rotation.y,rotation.z))



	def test(self): 

		self.reset_all()

		self.rotate('spine1', m.Quaternion((0.9651556611061096,0.0,-0.2616766095161438,-2.9802322387695312e-08)))




print('\n'*20)


path = '/home/mehdi/Code/PythonBlender/Animation/initial_pose'
sketelon = Skeleton(bpy.data.objects['Armature'], load = True, path = path)

sketelon.print_pose()

# sketelon.NierPunch2()
# sketelon.test()
# sketelon.NierDirect()
# sketelon.RunMale()
# sketelon.HitUppercut()
# sketelon.IdleCombat()