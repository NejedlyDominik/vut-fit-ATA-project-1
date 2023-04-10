#!/usr/bin/env python3
"""
ATA - Project 1 - Trolley control in a robotic factory

login: xnejed09
name: Dominik Nejedly
year: 2023

Test implementation based on the resulting CEG and Combine decision tables.
"""

from cartctl import CartCtl, Status
from cart import Cart, CargoReq
from jarvisenv import Jarvis
import unittest

def log(msg):
    """Simple logging"""
    print('  %s' % msg)

class TestCartRequests(unittest.TestCase):
    
    def setUp(self):
        """The setup phase of each test"""
        Jarvis.reset_scheduler()
        print('\n----------------------------------------------------------------------')
        print('Running test:', self._testMethodName)
        print('----------------------------------------------------------------------')
    
    @staticmethod
    def add_load(cart_ctl: CartCtl, cargo_req: CargoReq):
        """Callback for schedulled load"""
        log('Time: %d - Requesting %s at %s' % (Jarvis.time(), cargo_req, cargo_req.src))
        cart_ctl.request(cargo_req)
        
    @staticmethod
    def log_on_move(c: Cart):
        """Move logging"""
        log('Time: %d - Cart is moving %s->%s' % (Jarvis.time(), c.pos, c.data))
        
    @staticmethod
    def log_on_load(c: Cart, cargo_req: CargoReq):
        """Load logging"""
        log('Time: %d - Cart at %s - loading: %s' % (Jarvis.time(), c.pos, cargo_req))
        log(c)
        
    @staticmethod
    def log_on_unload(c: Cart, cargo_req: CargoReq):
        """Unload logging"""
        log('Time: %d - Cart at %s - unloading: %s' % (Jarvis.time(), c.pos, cargo_req))
        log(c)
         
    def test_happy(self):
        """Happy-path test"""

        def on_move(c: Cart):
            """Example callback (for assert)"""
            # put some asserts here
            self.log_on_move(c)

        def on_load(c: Cart, cargo_req: CargoReq):
            """Example callback for logging"""
            self.log_on_load(c, cargo_req)
            cargo_req.context = "loaded"

        def on_unload(c: Cart, cargo_req: CargoReq):
            """Example callback (for assert)"""
            # put some asserts here
            self.log_on_unload(c, cargo_req)
            self.assertEqual('loaded', cargo_req.context)
            cargo_req.context = 'unloaded'
            if cargo_req.content == 'helmet':
                self.assertEqual('B', c.pos)
            if cargo_req.content == 'heart':
                self.assertEqual('A', c.pos)
            #if cargo_req.content.startswith('bracelet'):
            #    self.assertEqual('C', c.pos)
            if cargo_req.content == 'braceletR':
                self.assertEqual('A', c.pos)
            if cargo_req.content == 'braceletL':
                self.assertEqual('C', c.pos)

        # Setup Cart
        # 4 slots, 150 kg max payload capacity, 2=max debug
        cart_dev = Cart(4, 150, 0)
        cart_dev.onmove = on_move

        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)

        # Setup Cargo to move
        helmet = CargoReq('A', 'B', 20, 'helmet')
        helmet.onload = on_load
        helmet.onunload = on_unload

        heart = CargoReq('C', 'A', 40, 'heart')
        heart.onload = on_load
        heart.onunload = on_unload

        braceletR = CargoReq('D', 'A', 40, 'braceletR')
        braceletR.onload = on_load
        braceletR.onunload = on_unload

        braceletL = CargoReq('D', 'C', 40, 'braceletL')
        braceletL.onload = on_load
        braceletL.onunload = on_unload

        # Setup Plan
        #         when  event     called_with_params
        Jarvis.plan(10, self.add_load, (cart_ctl, helmet))
        Jarvis.plan(45, self.add_load, (cart_ctl, heart))
        Jarvis.plan(40, self.add_load, (cart_ctl, braceletR))
        Jarvis.plan(25, self.add_load, (cart_ctl, braceletL))
        
        # Exercise + Verify indirect output
        #   SUT is the Cart.
        #   Exercise means calling Cart.request in different time periods.
        #   Requests are called by add_load (via plan and its scheduler).
        #   Here, we run the plan.
        Jarvis.run()

        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual('unloaded', helmet.context)
        self.assertEqual('unloaded', heart.context)
        self.assertEqual('unloaded', braceletR.context)
        self.assertEqual('unloaded', braceletL.context)
        #self.assertEqual(cart_dev.pos, 'C')
        
    def test_no_request(self):
        """
        Test the case where no request is scheduled.
        CEG - test case: 1
        """
        
        def on_move(c: Cart):
            "Callback for scheduled move"
            self.log_on_move(c)
            self.fail('The cart should not move.')
            
        # Setup Cart
        load_capacity = 50
        num_slots = 3
        cart_dev = Cart(num_slots, load_capacity, 0)
        cart_dev.onmove = on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertTrue(cart_dev.load_capacity, load_capacity)
        self.assertTrue(len(cart_dev.slots), num_slots)
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(cart_dev.pos, 'A')
        
    def test_all_slots_taken(self):
        """
        Test the case where all slots of a cart are taken.
        CEG - test case: 3
        """
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertEqual('lion', cargo_req.content)
            self.fail('Lion should not be loaded')
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual('lion', cargo_req.content)
            self.fail('Lion should not be unloaded')
                
        def check_req_prior_lion(cart_ctl: CartCtl):
            """Callback for lion request priority checking"""
            self.assertTrue(cart_ctl.requests)
            self.assertEqual('lion', cart_ctl.requests[0].content)
            self.assertTrue(cart_ctl.requests[0].prio)
            
        # Setup Cart
        cart_dev = Cart(1, 150, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('C', 'A', 15, 'flamingo')
        flamingo.onload = self.log_on_load
        flamingo.onunload = self.log_on_unload

        kangaroo = CargoReq('A', 'D', 70, 'kangaroo')
        kangaroo.onload = self.log_on_load
        kangaroo.onunload = self.log_on_unload

        lion = CargoReq('D', 'B', 140, 'lion')
        lion.onload = on_load
        lion.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(10, self.add_load, (cart_ctl, kangaroo))
        Jarvis.plan(12, self.add_load, (cart_ctl, lion))
        Jarvis.plan(80, check_req_prior_lion, (cart_ctl,))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        
    def test_overload(self):
        """
        Test the case where loading a request would cause exceeding the maximum load capacity.
        CEG - test case: 4
        """
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            
            if cargo_req.content == 'grizzly':
                self.assertGreater(Jarvis.time(), 60 + 10)
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            
            if cargo_req.content == 'kangaroo':
                self.assertLess(Jarvis.time(), 60 + 10)
                
        def check_req_prior_grizzly(cart_ctl: CartCtl):
            """Callback for grizzly request priority checking"""
            self.assertTrue(cart_ctl.requests)
            self.assertEqual('grizzly', cart_ctl.requests[0].content)
            self.assertTrue(cart_ctl.requests[0].prio)
            
        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        kangaroo = CargoReq('A', 'D', 130, 'kangaroo')
        kangaroo.onload = self.log_on_load
        kangaroo.onunload = self.log_on_unload
        
        grizzly = CargoReq('C', 'B', 400, 'grizzly')
        grizzly.onload = on_load
        grizzly.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, kangaroo))
        Jarvis.plan(10, self.add_load, (cart_ctl, grizzly))
        Jarvis.plan(80, check_req_prior_grizzly, (cart_ctl,))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        
    def test_load_request(self):
        """
        Test the case where a (standard) request is loaded.
        CEG - test case: 5
        """
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertEqual(cargo_req.content, 'flamingo')
            self.assertEqual(c.pos, 'B')
            self.assertIn(cargo_req, c.slots)
            self.assertFalse(cargo_req.prio)
            self.assertLess(Jarvis.time(), 60)
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.content, 'flamingo')
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertFalse(cargo_req.prio)
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual(c.pos, 'D')
            cargo_req.context = 'unloaded'
                
        def check_normal(cart_ctl: CartCtl):
            """Callback for Normal status checking"""
            self.assertEqual(Status.Normal, cart_ctl.status)
            
        # Setup Cart
        cart_dev = Cart(4, 50, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('B', 'D', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(10, check_normal, (cart_ctl,))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(cart_dev.pos, 'D')
        self.assertEqual(flamingo.context, 'unloaded')
        
    def test_load_prior_request(self):
        """
        Test the case where a request with the priority property is loaded.
        CEG - test case: 6
        """
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertTrue(cargo_req.prio)
            cargo_req.context = 'loaded'
            
            if cargo_req.content == 'flamingo':
                self.assertEqual(c.pos, 'D')
                self.assertLess(Jarvis.time(), 60 + 10)
            elif cargo_req.content == 'kangaroo':
                self.assertEqual(c.pos, 'A')
                self.assertGreater(Jarvis.time(), 60 + 10 + 60)
                self.assertLess(Jarvis.time(), 60 + 10 + 2 * 60)
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertTrue(cargo_req.prio)
            self.assertNotIn(cargo_req, c.slots)
            cargo_req.context = 'unloaded'
            
            if cargo_req.content == 'flamingo':
                self.assertEqual(c.pos, 'C')
            elif cargo_req.content == 'kangaroo':
                self.assertEqual(c.pos, 'B')
            
        def check_unload_only(cart_ctl: CartCtl):
            """Callback for UnloadOnly status checking"""
            self.assertEqual(Status.UnloadOnly, cart_ctl.status)
            
        def check_normal(cart_ctl: CartCtl):
            """Callback for Normal status checking"""
            self.assertEqual(Status.Normal, cart_ctl.status)
            
        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('D', 'C', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload

        kangaroo = CargoReq('A', 'B', 70, 'kangaroo')
        kangaroo.onload = on_load
        kangaroo.onunload = on_unload
        
        lion = CargoReq('C', 'B', 140, 'lion')
        lion.onload = self.log_on_load
        lion.onunload = self.log_on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(60, self.add_load, (cart_ctl, kangaroo))
        Jarvis.plan(60 + 10 + 30, check_unload_only, (cart_ctl,))
        Jarvis.plan(60 + 10 + 60 + 20, self.add_load, (cart_ctl,lion))
        Jarvis.plan(60 + 10 + 60 + 10 + 50, check_normal, (cart_ctl,))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertEqual(flamingo.context, 'unloaded')
        self.assertEqual(kangaroo.context, 'unloaded')
        
    def test_combine_1(self):
        """Combine - test case: 1"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertEqual(cargo_req.content, 'lion')
            self.fail('Lion should not be loaded')
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.content, 'lion')
            self.fail('Lion should not be unloaded')
                
        def check_req_prior_lion(cart_ctl: CartCtl):
            """Callback for lion request priority checking"""
            if cart_ctl.requests:
                # If the request is not removed from planned requests for efficiency, test that its priority is set.
                self.assertEqual('lion', cart_ctl.requests[0].content)
                self.assertTrue(cart_ctl.requests[0].prio)
            
        # Setup Cart
        cart_dev = Cart(1, 150, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        lion = CargoReq('B', 'B', 200, 'lion')
        lion.onload = on_load
        lion.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(20, self.add_load, (cart_ctl, lion))
        Jarvis.plan(100, check_req_prior_lion, (cart_ctl,))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(Status.Idle, cart_ctl.status)
        
    def test_combine_2(self):
        """Combine - test case: 2"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'grizzly'])
            self.assertEqual(c.pos, 'C')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'grizzly'])
            self.assertEqual(c.pos, 'D')
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(1, 500, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('C', 'D', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload
        
        grizzly = CargoReq('C', 'D', 350, 'grizzly')
        grizzly.onload = on_load
        grizzly.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(1, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(2, self.add_load, (cart_ctl, grizzly))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'D')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(flamingo.context, 'unloaded')
        self.assertEqual(grizzly.context, 'unloaded')
        
    def test_combine_3(self):
        """Combine - test case: 3"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'kangaroo'])
            self.assertEqual(c.pos, 'B')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'kangaroo'])
            
            if cargo_req.content == 'flamingo':
                self.assertEqual(c.pos, 'B')
            else:
                self.assertEqual(c.pos, 'C')
                
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('B', 'B', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload
        
        kangaroo = CargoReq('B', 'C', 40, 'kangaroo')
        kangaroo.onload = on_load
        kangaroo.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(10, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(11, self.add_load, (cart_ctl, kangaroo))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(flamingo.context, 'unloaded')
        self.assertEqual(kangaroo.context, 'unloaded')
        
    def test_combine_4(self):
        """Combine - test case: 4"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'kangaroo'])
            
            if cargo_req.content == 'flamingo':
                self.assertEqual(c.pos, 'A')
            else:
                self.assertEqual(c.pos, 'C')
            
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'kangaroo'])
            self.assertEqual(c.pos, 'B')              
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 150, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('A', 'B', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload
        
        kangaroo = CargoReq('C', 'B', 80, 'kangaroo')
        kangaroo.onload = on_load
        kangaroo.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(61, self.add_load, (cart_ctl, kangaroo))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'B')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(flamingo.context, 'unloaded')
        self.assertEqual(kangaroo.context, 'unloaded')
        
    def test_combine_5(self):
        """Combine - test case: 5"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertEqual(cargo_req.content, 'lion')
            self.assertEqual(c.pos, 'D')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertEqual(cargo_req.content, 'lion')
            self.assertEqual(c.pos, 'B')              
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 500, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        lion = CargoReq('D', 'B', 230, 'lion')
        lion.onload = on_load
        lion.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, lion))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'B')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(lion.context, 'unloaded')
        
    def test_combine_8(self):
        """Combine - test case: 8"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'koala'])
            self.assertEqual(c.pos, 'C')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['flamingo', 'koala'])
            self.assertEqual(c.pos, 'C')              
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(3, 50, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move
        flamingo = CargoReq('C', 'C', 15, 'flamingo')
        flamingo.onload = on_load
        flamingo.onunload = on_unload
        
        koala = CargoReq('C', 'C', 25, 'koala')
        koala.onload = on_load
        koala.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, flamingo))
        Jarvis.plan(61, self.add_load, (cart_ctl, koala))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'C')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(flamingo.context, 'unloaded')
        self.assertEqual(koala.context, 'unloaded')
        
    def test_combine_9(self):
        """Combine - test case: 9"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'turtle'])
            self.assertEqual(c.pos, 'A')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'turtle'])
            
            if cargo_req.content == 'koala':           
                self.assertEqual(c.pos, 'C')
            else:
                self.assertEqual(c.pos, 'B')
      
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move        
        koala = CargoReq('A', 'C', 25, 'koala')
        koala.onload = on_load
        koala.onunload = on_unload
        
        turtle = CargoReq('A', 'B', 40, 'turtle')
        turtle.onload = on_load
        turtle.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, koala))
        Jarvis.plan(61, self.add_load, (cart_ctl, turtle))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'B')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(koala.context, 'unloaded')
        self.assertEqual(turtle.context, 'unloaded')
        
    def test_combine_10(self):
        """Combine - test case: 10"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'lion'])
            self.assertEqual(c.pos, 'B')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'lion'])        
            self.assertEqual(c.pos, 'D')      
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(1, 150, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move        
        koala = CargoReq('B', 'D', 25, 'koala')
        koala.onload = on_load
        koala.onunload = on_unload
        
        lion = CargoReq('B', 'D', 140, 'lion')
        lion.onload = on_load
        lion.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, koala))
        Jarvis.plan(61, self.add_load, (cart_ctl, lion))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'D')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(koala.context, 'unloaded')
        self.assertEqual(lion.context, 'unloaded')
        
    def test_combine_11(self):
        """Combine - test case: 11"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['lion', 'grizzly'])
            self.assertEqual(c.pos, 'D')
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['lion', 'grizzly'])        
            self.assertEqual(c.pos, 'D')      
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(1, 500, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move               
        lion = CargoReq('D', 'D', 150, 'lion')
        lion.onload = on_load
        lion.onunload = on_unload
        
        grizzly = CargoReq('D', 'D', 450, 'grizzly')
        grizzly.onload = on_load
        grizzly.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, lion))
        Jarvis.plan(61, self.add_load, (cart_ctl, grizzly))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(cart_dev.pos, 'D')
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(lion.context, 'unloaded')
        self.assertEqual(grizzly.context, 'unloaded')
        
    def test_combine_12(self):
        """Combine - test case: 12 (with number of slots adjusted to 2)"""
        
        def on_load(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled loading"
            self.log_on_load(c, cargo_req)
            self.assertIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'turtle'])
            
            if cargo_req.content == 'koala':
                self.assertEqual(c.pos, 'C')
            else:
                self.assertEqual(c.pos, 'A')
                
            cargo_req.context = 'loaded'
                  
        def on_unload(c: Cart, cargo_req: CargoReq):
            "Callback for scheduled unloading"
            self.log_on_unload(c, cargo_req)
            self.assertEqual(cargo_req.context, 'loaded')
            self.assertNotIn(cargo_req, c.slots)
            self.assertIn(cargo_req.content, ['koala', 'turtle'])        

            if cargo_req.content == 'koala':
                self.assertEqual(c.pos, 'C')
            else:
                self.assertEqual(c.pos, 'D')
   
            cargo_req.context = 'unloaded'
            
        # Setup Cart
        cart_dev = Cart(2, 50, 0)
        cart_dev.onmove = self.log_on_move
        
        # Setup Cart Controller
        cart_ctl = CartCtl(cart_dev, Jarvis)
        
        # Setup Cargo to move               
        koala = CargoReq('C', 'C', 25, 'koala')
        koala.onload = on_load
        koala.onunload = on_unload
        
        turtle = CargoReq('A', 'D', 40, 'turtle')
        turtle.onload = on_load
        turtle.onunload = on_unload
        
        # Setup Plan
        Jarvis.plan(0, self.add_load, (cart_ctl, koala))
        Jarvis.plan(0, self.add_load, (cart_ctl, turtle))
        
        # Exercise + Verify indirect output
        Jarvis.run()
        
        # Verify direct output
        log(cart_dev)
        self.assertTrue(cart_dev.empty())
        self.assertEqual(Status.Idle, cart_ctl.status)
        self.assertEqual(turtle.context, 'unloaded')
        
if __name__ == "__main__":
    unittest.main()
