"""Plain-English sample texts for testing the substitution cracker.

Hand-written, one distinct passage for every length from 50 to 400
characters in steps of 5 (71 texts). All original sentences on varied
topics so each entry differs as much as possible; each is trimmed to its
exact character length. Real English letter/quadgram statistics — use
them to chart cracker recovery against ciphertext length.

    from data.sample_texts import TEXTS_BY_LENGTH, SAMPLE_TEXTS
"""

# {length_in_chars: text}
TEXTS_BY_LENGTH = {
    50: 'The morning fog rolled in from the cold grey seas.',
    55: 'A small wooden boat drifted slowly past the old harbour',
    60: 'The tired old librarian shelved the very last book and quiet',
    65: 'Rain tapped softly at the dark window while the old kettle slowly',
    70: 'He counted the small coins twice over, then slipped them into his worn',
    75: 'The laughing children raced across the wide meadow chasing the last warm li',
    80: 'She wrote a short careful letter to her brother and posted it just before the sm',
    85: 'The train was running late once again, so the weary travelers waited beneath the flic',
    90: 'A thin bright layer of frost covered the whole garden, and the cold morning air smelled of',
    95: 'The young musician tuned her old violin very slowly, listening hard for the single note that wo',
    100: 'Far out on the wide open plain the great herd moved as one body, raising a low brown cloud of dust a',
    105: 'The baker rose long before the grey dawn, kneading the pale soft dough by lamplight until the whole quiet',
    110: 'Down at the quay the fishermen mended their salt-stiff nets, talking quietly about the catch and the coming ga',
    115: 'The astronomer leaned close to the eyepiece, holding her breath as a faint smear of light slowly resolved into a sp',
    120: 'In the cluttered workshop the carpenter ran his thumb along the grain, judging where the plane should bite into the roug',
    125: 'The river turned the mossy wheel of the old mill all year, and the grey miller still climbed the worn stone steps at every da',
    130: 'High on the ridge the climbers paused in the thin air, watching the valley fill with cloud while the cold sun burned white above t',
    135: 'By midmorning the market square was loud with bargaining, baskets of bruised fruit, the clang of a coppersmith, and the smell of bread ',
    140: 'The teacher wrote a single question on the board, then sat in silence at the back of the room and let the long, awkward quiet do the patient',
    145: 'In the narrow studio the painter mixed a grey from blue and burnt orange, stepped back, frowned at the canvas, and scraped the whole morning away',
    150: 'When the storm finally broke the old sailor lashed himself to the wheel, shouting orders the wind tore away, while green water climbed the deck and th',
    155: 'The farmer walked his fields at first light, pressing the dry soil between his fingers and watching the sky for the rain that the long, brittle summer had ',
    160: "Inside the clockmaker's shop a hundred small movements ticked slightly out of step, so the room seemed to breathe, and the old man bent over his bench never onc",
    165: 'The bees moved heavily between the late flowers of the garden, and the warm afternoon hummed with their work, while a single thrush practised the same three notes fr',
    170: 'The caravan crossed the dunes for nine days, the camels swaying under their loads, and at night the traders sat close to the small fire and told the old stories the deser',
    175: 'Deep in the archive the historian unfolded a brittle map, holding the lamp away from the dry paper, and traced with one careful finger a road that had not carried a single tra',
    180: 'In the orchard the long rows of trees had begun to turn, and the windfall apples lay bruised and fragrant in the wet grass, while wasps drifted slow and drunk through the heavy gol',
    185: 'The blacksmith worked the bellows until the coals glowed white, then drew the iron out in a shower of sparks and beat it on the anvil with a steady ringing that carried far down the emp',
    190: 'The lighthouse keeper climbed the iron stair twice each night to trim the wick and polish the great lens, and in the long dark hours between he wrote careful notes about the weather, the tid',
    195: 'Snow fell on the small mountain village all through the night, softening the roofs and the narrow lanes, and by morning the only sound was a shovel somewhere, scraping, and the muffled clang of t',
    200: 'The scientist checked the dial a third time, certain she had made an error, but the needle held its impossible reading, and for one long electric moment she knew that the careful work of twenty quiet ',
    205: 'The train carried them slowly through the green countryside, past hedgerows and grazing sheep and small stone bridges, and the two old friends said almost nothing, content to watch the soft afternoon slide',
    210: "In the attic of the old house they found trunks of yellowing letters, a cracked violin, a box of faded photographs, and a child's wooden horse, and each object seemed to hold its breath, waiting to tell some fo",
    215: 'The city softened as the evening came on, the hard noise of the day giving way to lit windows and the smell of cooking, and along the river the lamps came on one by one until the dark water carried a long broken rib',
    220: 'The narrow path wound deeper into the forest, and the light grew green and dim beneath the high canopy, while somewhere far off a stream talked over its stones and the still air smelled of moss, wet bark, and the slow pa',
    225: "For three weeks the small ship beat westward against the swell, and the crew grew lean and quiet, until one grey morning a single gull wheeled out of the mist, and then another, and the lookout's hoarse cry of land brought ev",
    230: 'The travellers reached the ancient ruins at noon and stood in silence among the broken columns, where lizards basked on the fallen stone and the wind moved through the empty doorways, carrying the dry whisper of a city that had be',
    235: 'The winter cabin smelled of pine smoke and old wool, and outside the snow came down thick and steady through the blue dusk, so they fed the stove, lit the single lamp, and settled in to wait out the long storm with a kettle, a worn pac',
    240: 'The little jazz club was half full and full of smoke, and when the trumpet finally came in over the slow brushed drums the whole room seemed to lean forward, and even the bored waiter stopped at the bar to listen, glass in hand, until the l',
    245: 'The vineyard ran in long green rows down the south-facing slope, and in the heavy heat of late summer the pickers moved slowly between the vines, filling their baskets and calling to one another, while the dust hung gold in the air and the far h',
    250: 'Out in the desert the night sky was so crowded with stars that the old constellations were hard to find, and lying back on the still-warm sand the children grew quiet at last, awed by the great silent wheel of light turning slowly overhead while the ',
    255: 'Before the sun was fully up the fishing village had already come awake, with nets spread to dry on the sea wall, the smell of tar and salt and frying fish, gulls quarrelling over the gutting tables, and the small painted boats riding low and patient in th',
    260: 'The lecture hall was old and steep and cold, and the professor spoke without notes, filling board after board with quick chalk diagrams, and though half the students were hopelessly lost within ten minutes a few sat very still, sensing that they were watching ',
    265: 'The mountain lake lay perfectly still in the early light, a flawless mirror of grey peaks and pale sky, until a single fish rose and broke the surface, and the rings spread out and out across the cold dark water, slowly blurring the reflected mountains before the g',
    270: 'The medieval town climbed the hill in a tangle of crooked streets, and from the worn ramparts you could see the river, the patchwork fields, and the dark line of the forest beyond, while below in the square a stone fountain splashed and the old cathedral bells began, as',
    275: 'The spice market was a riot of colour and smell, with open sacks of saffron, cumin, and dried red chillies, with traders shouting their prices over one another, the steady tap of a coppersmith somewhere close by, and the thick, warm, dizzying air that seemed to hold a hundre',
    280: 'The polar expedition had been trapped in the ice for months, and the long darkness wore steadily at the men, but the captain kept them busy with watches, repairs, and careful records, and on the clear nights they would climb out onto the frozen deck to watch the green fire of the',
    285: 'The river delta spread wide and shallow toward the sea, a great maze of reed beds and slow brown channels, and at dawn it came alive with birds, thousands upon thousands of them, rising in great shifting clouds, wheeling and settling and rising again, until the whole flat horizon seem',
    290: 'High on the dark mountain the observatory dome turned with a low hum, and inside the astronomer worked alone through the cold small hours, guiding the great mirror, gathering the faint ancient light of galaxies so distant that the glow she patiently recorded that night had begun its long j',
    295: 'The country wedding spilled out of the small stone church into the orchard, where long tables had been set under the trees, and there was cider and fiddle music and dancing on the trodden grass, and the old people sat in the shade smiling at it all, and the children ran wild among the guests un',
    300: 'When the ship finally went down the survivors crowded into two small boats, and for nine long days they rowed and bailed and rationed the last of the water, watching the empty horizon, until on the tenth grey morning the youngest among them slowly stood, pointed with a shaking hand, and croaked out ',
    305: 'The botanical garden held glasshouses from every climate, and stepping from the cold spring afternoon into the great palm house was like crossing the whole world in a single stride, into wet heat and green shadow and the steady drip of unseen water, where vast leaves arched overhead and the air itself wa',
    310: 'The railway pushed north through the mountains for six long hard years, and the work cost the company a fortune and the men far more, blasting tunnels through the solid rock, throwing iron bridges across the deep gorges, and laying mile after patient mile of track, until at last a single thin line of steel jo',
    315: 'The archaeologists worked through the hottest part of the long season, brushing the desert sand away grain by grain from the buried floor, and just as the light was failing on the last planned day a corner of painted plaster appeared, and then a hand, and then a face, and the whole tired team gathered in silence a',
    320: 'The alpine meadow was a single sheet of flowers in the brief mountain summer, blue and yellow and white from the last of the melting snow to the grey scree above, and the warm air droned with insects and the music of cowbells, while far below the valley still lay in shadow and the high peaks held the sun long after the',
    325: 'When the storm drove the heavy freighter onto the rocks the lifeboat crew put out at once into the black, screaming night, and for two long hours they fought the breaking seas, soaked and frozen and half blind with the flying spray, until at last they came alongside the wreck and began, one by one, to haul the exhausted sai',
    330: 'The invention of the printing press changed the whole world more quietly than any war, for once a single careful setting of type could throw off a thousand identical pages, books quickly ceased to be the rare treasures of the few, and ideas, true and false alike, began to travel faster and very much further than any king or chur',
    335: 'The tea plantation covered the green hills in neat curving rows, and in the cool of the early morning the pickers moved steadily along them with broad baskets on their backs, their quick fingers flicking out the youngest leaves with a speed that looked almost like magic, while the mist still lay in the valleys and the far ridges floa',
    340: 'The research station sat alone on the great white plain, a small cluster of huts and aerials under a sky that stayed dark for months on end, and the little team inside kept to a careful daily routine of measurements and meals and sleep, bound together by the work and the cold and the simple knowledge that, for a thousand empty miles in ev',
    345: 'In the crowded renaissance workshop the master moved from bench to bench, correcting a line here and mixing a pigment there, while a dozen young apprentices ground colours, prepared panels, and copied his drawings over and over again, learning with their hands what no book could ever teach, until one day the most gifted among them would quietl',
    350: 'The submersible sank slowly into the dark, and the last of the blue light faded from the portholes until there was nothing outside but the black water and the pale drift of falling specks, and then, two whole miles down on the cold floor of the sea, the lights picked out a strange still garden of pale corals and blind white crabs, life thriving pat',
    355: 'The homestead stood quite alone on the wide prairie, a low house and a windmill and a thin line of planted trees against a sky that seemed to go on forever, and through the first few hard winters the family slowly learned the moods of that great empty land, its sudden blizzards and grass fires and spring floods, until season by patient season the raw cl',
    360: "The cathedral took three long centuries to build, and the masons who laid down its first deep foundations knew with perfect certainty that they would never live to see it finished, nor would their children, nor their children's children, and yet still they cut each hidden stone with the very same patient care, trusting the slow work to hands not yet born and",
    365: 'The expedition followed the great brown river deep into the jungle for many weeks, the heat and the insects and the green walls of forest pressing in on every side, and each night they camped on a narrow muddy bank and lay listening to the vast living darkness around them, the screams and clicks and sudden silences, feeling with every slow mile just how very far ',
    370: 'The monastery clung to the bare mountainside high above the clouds, reached only by a long stair cut straight into the living rock, and the monks who lived up there had faithfully kept the same quiet round of prayer and work and study for well over a thousand years, copying out their books by hand, tending their thin terraced gardens, and ringing the deep bell into th',
    375: 'All through the wild and roaring night the lighthouse threw its slow bright beam out across the breaking seas, and the keeper stood at the high window watching for the small fishing fleet that had not yet come safely home, and when at last, near morning, he had counted the boats one by one past the dark headland and into the calm of the harbour, he let out a long slow brea',
    380: 'The grand old library rose in tier upon tier of dark polished shelves toward a painted ceiling far overhead, and the deep hush inside it was almost a living thing, broken only now and then by the turn of a single page or a soft footstep on the iron stair, and a reader who looked up from his book could feel, in the patient ranks of a million crowded spines, the gathered thought ',
    385: 'The little band of explorers reached the oasis at the very last edge of their strength, and at the first sight of the palms and the still green pool the camels broke into a stumbling run, and the men fell from the saddles and lay full length in the cool shade, far too parched even to speak, while the quiet keepers of the wells came out unhurried to meet them, bearing water in heavy ',
    390: 'The volcanic island had risen out of the sea within living memory, born in fire and steam within plain sight of the fishing boats, and now, only a single lifetime later, it lay green and breathing under the sun, its black rock already softened by moss and fern and the first stubborn trees, its high cliffs loud with nesting birds, a whole small world conjured up from nothing, a quiet proo',
    395: 'The winter expedition set out across the frozen plateau hauling everything they owned behind them on long heavy sledges, and for a month they marched on into the wind through a white nothing, the horizon and the sky a single seamless grey, navigating by the compass alone, until the cold and the endless labour had worn them down to a stubborn animal rhythm of hauling and camping and sleeping, ',
    400: 'The harvest festival filled the whole village square from early morning until long past dark, with trestle tables groaning under fresh bread and roast meat and great heavy wheels of cheese, with music and dancing and the shy first words of young couples, and when the tall bonfire was finally lit the whole community gathered in close around it, the warm firelight on their tired and happy faces, giv',
}

# Same texts as a plain list, ordered short -> long.
SAMPLE_TEXTS = list(TEXTS_BY_LENGTH.values())
