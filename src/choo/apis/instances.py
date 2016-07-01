from .efa import EFA

vrr = EFA(name='vrr', base_url='http://efa.vrr.de/standard/', preset='de')
# vrr = EFA('vrr', 'http://app.vrr.de/companion-vrr/')
vrn = EFA(name='vrn', base_url='http://fahrplanauskunft.vrn.de/vrn/', preset='de')
