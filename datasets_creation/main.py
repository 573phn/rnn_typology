from utils import *
import agreement_collector
import agreement_markers
import argparse


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--print-txt', type=int, choices=[1,0], help = "if 1 prints modified sentences as textfile", required = False, default = False, dest = "print_txt")
	parser.add_argument('--dataset', type=str, choices=["train", "dev", "test", "control"], help = "train/dev/test", required = True, dest = "dataset")
	parser.add_argument('--agreement-marker', type=str, choices=['na-d','na-d-3dec','na-s','na-a', 'ea-d','ea-s','ea-a'], help = "agreement marker. na-d: nominative accusative, deterministic; na-s: nominative accusative,syncretistic; na-a: nominative accusative, fully ambigious; ea-d: ergative absolutive, deterministic; ea-s: ergative absolutive, syncretistic; ea-a: ergative absolutive, fully ambigious", required = True, dest = "agreement_marker")
	parser.add_argument('--add-cases', type=int, choices=[1, 0], help = "whether or not to explicitly mark cases", required = True, dest = "add_cases")

	parser.add_argument('--order', type=str, choices=["sov", "svo", "ovs", "osv", "vso", "vos", "random", "vso60rest8", "vso30rest14", "vos60rest8", "vos30rest14"], help = "word order", required = True)
	
	parser.add_argument('--nsubj', type=int, choices=[1,0], help = "whether or not to include subject-verb agreement", required = False, default = True)
	parser.add_argument('--dobj', type=int, choices=[1,0], help = "whether or not to include object-verb agreement", required = False, default = True)
	parser.add_argument('--iobj', type=int, choices=[1,0], help = "whether or not to include indirect-object-verb agreement", required = False, default = True)
	parser.add_argument('--mark-verb', type=int, choices=[1,0], help = "whether or not to add agreement marking to verbs", required = False, default = True, dest = "mark_verb")
	parser.add_argument('--lemmatize', type=int, choices=[1,0], help = "whether or not to lemmatize verbs (before possible addition of artificial case suffixes)", required = False, default = True)
	
	parser.add_argument('--filter-no-att', type=int, choices=[1,0], help = "whether to filter out agreement instances without subject-verb attractors", required = False, default = False, dest = "filter_no_att")
	parser.add_argument('--filter-att', type=int, choices=[1,0], help = "whether to filter out agreement instances with subject-verb attractors", required = False, default = False, dest = "filter_att")                        
	parser.add_argument('--filter-obj', type=int, choices=[1,0], help = "whether to filter sentences with direct object", required = False, default = False, dest = "filter_obj") 
	parser.add_argument('--filter-no-obj', type=int, choices=[1,0], help = "whether to filter sentences without direct object", required = False, default = False, dest = "filter_no_obj")
	parser.add_argument('--filter-obj-att', type=int, choices=[1,0], help = "whether to filter sentences with subject-verb object attractor", required = False, default = False, dest = "filter_obj_att") 
	parser.add_argument('--filter-no-obj-att', type=int, choices=[1,0], help = "whether to filter sentences without subject-verb object attractor", required = False, default = False, dest = "filter_no_obj_att") 
	
	parser.add_argument('--random-seed', type=int, help="random seed to use", required=False, default=5, dest="random_seed") 
	
	args = parser.parse_args()
	
	add_cases = args.add_cases
	
	if args.agreement_marker == "na-d":           
		agreement_marker = agreement_markers.NominativeAccusativeMarker(add_cases = add_cases)
	elif args.agreement_marker == "na-d-3dec":
		agreement_marker = agreement_markers.NominativeAccusativeMarker3Decl(add_cases = add_cases)
	elif args.agreement_marker == "na-s":
		agreement_marker = agreement_markers.AmbigiousNominativeAccusativeMarker(add_cases = add_cases)
	elif args.agreement_marker == "na-a" or args.agreement_marker == "ea-a":
		agreement_marker = agreement_markers.ArgumentPresenceMarker(add_cases = add_cases)
	elif args.agreement_marker == "ea-d":      
		agreement_marker = agreement_markers.ErgativeAbsolutiveMarker(add_cases = add_cases)
	elif args.agreement_marker == "ea-s":
		agreement_marker = agreement_markers.AmbigiousNominativeAccusativeMarker(add_cases = add_cases)		
		
	agreements =  {"nsubj": True, "dobj": True, "obj": True, "iobj": True}
	argument_types = None # ["NNS", "NNP"]
	verbs = None# ["VBP", "VBZ"]
	
	collector = agreement_collector.AgreementCollector(mode=args.dataset, skip = 1, agreement_marker = agreement_marker, order = args.order, agreements = agreements, argument_types = argument_types, verbs = verbs, most_common = 200000, mark_verb = args.mark_verb, lemmatize_verbs = args.lemmatize, fname = "data/" + args.dataset + "-penn-ud.zip", replace_uncommon  = False, add_gender = False, filter_no_att = args.filter_no_att, filter_att = args.filter_att, filter_obj = args.filter_obj, filter_no_obj= args.filter_no_obj, filter_obj_att = args.filter_obj_att, filter_no_obj_att = args.filter_no_obj_att, print_txt = args.print_txt, random_seed = args.random_seed)
	collector.collect_agreement()
