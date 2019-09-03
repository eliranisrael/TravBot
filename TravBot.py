from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import _pickle as pickle
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import smtplib
import time


def send_email(header, subject):

    from_addr = "reuevn@gmail.com"
    to_addr_list = ["reuevn@gmail.com"]

    message = f"Subject: {header}\n\n{subject}"

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login("reuevn@gmail.com", "ihmxzbqymhrlskdg")
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()


def read_file(file_name):
    with open(f"{file_name}.file", "rb") as rf:
        data = pickle.load(rf)
        return data


def write_file(file_name, data_to_write):
    with open(f"{file_name}.file", "wb") as wf:
        pickle.dump(data_to_write, wf)


class WebActions:

    def __init__(self, user, password):
        self.user = user

        self.browser = webdriver.Chrome("chromedriver.exe")

        if user:
            self.browser.get("https://ts1.travian.co.il/login.php?name={}&password={}".format(user, password))
        else:
            self.browser.get("https://ts1.travian.co.il/login.php")

    #  NEED TO FIX
    def add_user(self, username, password):
        """
        adds user to the users_dic and making a new folder for this user.
        """
        with open("users_dic.file", "rb") as rf:
            users_dic = dict(pickle.load(rf))

        users_dic[username] = password

        with open("users_dic.file", "wb") as wf:
            pickle.dump(users_dic, wf)

        path = os.path.dirname(os.path.realpath(__file__)) + '\\users\{}'.format(username)
        if not os.path.isdir(path):
            os.makedirs(path)

    def send_spy(self, targetX, targetY, spy_amount, mode=False):
        """
        :param targetX: (int)
        :param targetY: (int)
        :param spy_amount: (int)
        :param mode: False = resources info (default), True = defence info. (bool)
        """
        self.browser.get(f"https://ts1.travian.co.il/build.php?gid=16&tt=2&x={targetX}&y={targetY}&c=4&t4={spy_amount}")
        self.browser.find_element_by_name("s1").click()
        if mode:
            self.browser.find_element_by_xpath("//*[@type='radio'][@value='2']").click()
        self.browser.find_element_by_name("s1").click()

    def send_troops(self, targetX, targetY, troops, mode=4):
        """
        :param targetX: (int)
        :param targetY: (int)
        :param mode: 2 for reinforcement, 3 for full attack, 4 for raid (default)
        :param troops: (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11). (tuple)
                       (t1, t2, t3, t4, t5, t6, rams, catapults, managers, settlers, hero)
        """
        troops_str = ""
        for i in range(11):
            if troops[i]:
                troops_str += f"&t{i+1}={troops[i]}"

        self.browser.get(f"https://ts1.travian.co.il/build.php?id=39&tt=2&x={targetX}&y={targetY}&c={mode}{troops_str}")
        self.browser.find_element_by_name("s1").click()
        self.browser.find_element_by_name("s1").click()

    def get_current_village(self):
        ob = self.browser.find_element_by_xpath(
            "//div[3]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li[@class = ' active']/a[@class = 'active']")
        a, b = (str(ob.get_attribute("href")) + "&a").split("newdid=")
        c = b.split("&")
        return c[0]

    def go_to_village(self, newdid):
        self.browser.get("https://ts1.travian.co.il/dorf1.php?newdid={}&".format(newdid))

    #  FIX FOR REINFORCEMENTS
    def get_current_troops(self):
        """
        :return: a dictionary with keys as troops's number (int) and values as amount (int).
                 for example: {5: 54} => there are 54 t5.
        """
        troop_dic = {}
        troop_lst = [0]*11
        tbody = self.browser.find_elements_by_xpath("//body/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div[3]/div[3]/div[10]/table/tbody/tr")
        for i in range(len(tbody)):
            xpath = "//body/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div[3]/div[3]/div[10]/table/tbody/tr[{}]/td/a/img".format(i + 1)
            t_type = self.browser.find_element_by_xpath(xpath)
            a, t_type = t_type.get_attribute("class").split("unit u")
            if t_type == "hero":
                t_type = 11
            xpath = "//body/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div[3]/div[3]/div[10]/table/tbody/tr[{}]/td[@class='num']".format(
                i + 1)
            unit_amount = self.browser.find_element_by_xpath(xpath)
            troop_dic[int(t_type)] = int(unit_amount.text)
            try:
                troop_lst[int(t_type)-1] = int(unit_amount.text)
            except:
                pass
        troops = tuple(troop_lst)

        return troop_dic, troops

    #  NEED TO FIX
    def get_villages(self):
        """
                       ***           FIX THIS     >>>>>>>>>    ~~~~~need to cancel this one.~~~~~
        *** creates a folder for each village if one's not exist ^^^and it's base files.^^^ ***
        :return: a list of Villages.
        """
        villages_dic = {}
        ul = self.browser.find_elements_by_xpath("//body/div[3]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li")

        for i in range(len(ul)):
            xpatha = "//body/div[3]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li[{}]/a".format(i + 1)
            xpathdiv = "//body/div[3]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/ul/li[{}]/a/div[@class='name']".format(i + 1)
            b, newdid = self.browser.find_element_by_xpath(xpatha).get_attribute("href")[:-1].split("newdid=")
            name = self.browser.find_element_by_xpath(xpathdiv).get_attribute("textContent")
            villages_dic[name] = newdid

            path = os.path.dirname(os.path.realpath(__file__)) + "\\users\\{}\\{}".format(self.user, newdid)
            if not os.path.exists(path):
                os.makedirs(path)
                lst = []
                with open(path + "\\raid_list.file", "w"):
                    pass
                with open(path + "\\build_list.file", "w"):
                    pass
                with open(path + "\\route_list.file", "w"):
                    pass

        return villages_dic

    def send_resources(self, source_newdid, targetX, targetY, resources):
        """
        :param source_newdid: (int)
        :param targetX: (int)
        :param targetY: (int)
        :param resources: (wood, clay, iron, crop). (tuple)
        """
        self.browser.get(f"https://ts1.travian.co.il/build.php?newdid={source_newdid}&gid=17&t=5&x={targetX}&y={targetY}")
        r = [0] * 4
        for i in range(0, 4):
            r[i] = self.browser.find_element_by_id(f"r{i + 1}")
            r[i].send_keys(resources[i])
        self.browser.find_element_by_id("enabledButton").click()
        time.sleep(0.01)
        self.browser.find_element_by_id("enabledButton").click()

    def get_hourly_production(self):
        """
        :return: (wood, clay, iron, crop). (tuple)
        """
        lst = []
        for i in range(1, 5):
            tr = self.browser.find_element_by_xpath(f"//*[@id='production']/tbody/tr[{i}]/td[@class='num']").get_attribute("outerText")
            lst.append(int(tr[1:-1]))

        return tuple(lst)

    def get_trader_capacity(self):
        """
        :return: (int)
        """
        self.browser.get("https://ts1.travian.co.il/build.php?t=5&gid=17")
        return self.browser.find_element_by_xpath("//*[@id='addRessourcesLink1']").text

    #     def get_time_limited_resource_bonuses(self):

    # pass

    def get_available_resources(self):
        """
        :return: (wood, clay, iron, crop). (tuple)
        """
        lst = []
        for i in range(1, 5):
            lst.append(int(self.browser.find_element_by_xpath(f"//*[@id='l{i}']").text.replace(".", "")))

        return tuple(lst)

    def set_trade_proposal(self, sell, buy, sell_amount, buy_amount, time_limit=None, alliance_only=False):
        """
        :param sell: 1=wood, 2=clay, 3=iron, 4=crop. (int)
        :param buy: 1=wood, 2=clay, 3=iron, 4=crop. (int)
        :param buy_amount: (int)
        :param sell_amount: (int)
        :param time_limit: (int)
        :param alliance_only: (boolean)
        """
        self.browser.get(f"https://ts1.travian.co.il/build.php?gid=17&t=2")
        sell_box = self.browser.find_element_by_name("m1")
        buy_box = self.browser.find_element_by_name("m2")

        self.browser.find_element_by_xpath(f"//select[@name='rid1']/option[@value='{sell}']").click()
        self.browser.find_element_by_xpath(f"//select[@name='rid2']/option[@value='{buy}']").click()

        sell_box.send_keys(sell_amount)
        buy_box.send_keys(buy_amount)

        if time_limit is not None:
            time_limit_checkbox = self.browser.find_element_by_name("d1")
            time_limit_checkbox.click()
            time_limit_textbox = self.browser.find_element_by_name("d2")
            time_limit_textbox.clear()
            time_limit_textbox.send_keys(time_limit)

        if alliance_only:
            self.browser.find_element_by_name("ally").click()

        self.browser.find_element_by_css_selector("button[type='submit']").click()

    #  NEED TO FINISH
    def buy_trade_proposal(self, sell_type, buy_type, sell_amount, buy_amount, buy_from_username=None):
        """
        :param sell_type: 1=wood, 2=clay, 3=iron, 4=crop. (int)
        :param buy_type: 1=wood, 2=clay, 3=iron, 4=crop. (int)
        :param buy_amount: (int)
        :param sell_amount: (int)
        :param buy_from_username: (string)
        """
        self.browser.get(f"https://ts1.travian.co.il/build.php?gid=17&t=1&s={buy_type}&b={sell_type}")

        # NEED TO LOOP OVER MULTIPLE PAGES.
        table = self.browser.find_element_by_css_selector("table[id='range']")

        deals = table.fint_elements_by_xpath("//tbody/tr")

        if buy_from_username is not None:
            for deal in deals:
                if deal.find_element_by_css_selector("//td[class='pla']/a").get_attribute("textContent") != buy_from_username:
                    del deal

        # TESTING ~~~~ DELETE
        for deal in deals:
            print(deal.find_element_by_css_selector("//td[class='pla']/a").get_attribute("textContent"))

    def celebrate(self, mode="big"):
        """
        :param mode: "big"/"small" celebration. (string)
        """
        pass

    def is_current_village_under_attack(self):
        pass

    def get_gid(self):
        """
        works only in the window that opens right after you enter the building.
        :return: gid. (string)
        """
        data = self.browser.find_element_by_xpath("//*[@id='build']").get_attribute("class").split(" ")
        gid = data[0][3:]
        return gid

    def get_id(self):
        """
        works only in the window that opens right after you enter the building.
        :return: id. (string)
        """
        data = self.browser.current_url.split("id=")
        data = data[1]
        id = data
        return id

    def get_tribe(self):
        """
        :return: the tribe's name. (string)
        """
        tribe = ""
        return tribe


class Village:

    def __init__(self, username, newdid, status="feeder"):
        """
        :type username: (srting)
        :param newdid: (int)
        :param status: off/def/feed (string)
        """
        self.username = username
        self.newdid = newdid
        self.status = status
        self.name = self.get_name()
        self.x, self.y, self.z = self.get_coordinates()
        self.trader_capacity = self.get_trader_capacity()
        self.hourly_production = self.get_hourly_production()
        self.time_limited_resource_bonuses = self.get_time_limited_resource_bonuses()
        self.available_resources = self.get_available_resources()
        self.available_troops = self.get_available_troops()
        self.farm_list = self.get_farm_list()
        self.build_list = self.get_build_list()
        self.trading_routes = self.get_trading_routes()
        self.reinforcements = self.get_reinforcements()
        self.balance = 0  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TODO

    def get_name(self):
        """
        :return: the name of the village.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        name = ""  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return name

    def get_coordinates(self):
        """
        :return: the coordinates of the village.
                 (x,y,z)
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        x, y, z = 0, 0, 0
        return x, y, z

    def get_trader_capacity(self):
        """
        :return: the capacity of the village's trader.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        capacity = ""  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return capacity

    def get_hourly_production(self):
        """
        :return: the current production of the village, ignoring time limited bonuses. (tuple)
                 (wood, clay, iron, crop)
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return (0, 0, 0, 0)

    def get_time_limited_resource_bonuses(self):
        """
        :return: the current percentage of time limited bonuses to each resource, and it's time left.
                 e.x. (25, 0, 0, 25)
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return (0, 0, 0, 0)

    def get_available_resources(self):
        """
        :return: the current available resources. (tuple)
                 e.x. (12437, 723, 14, 31234)
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return (0, 0, 0, 0)

    def get_available_troops(self):
        """
        :return: the current available troops. (tuple)
                 (t1, t2, ... , t10, t11)
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        return (0, 0, 0, 0)

    def get_reinforcements(self):
        """
        :return: the village's reinforcements.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        reinforcements = 0
        return reinforcements

    def get_farm_list(self):
        """
        :return: the village's farm_list.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        farm_list = 0
        return farm_list

    def get_build_list(self):
        """
        :return: the village's build_list.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        build_list = 0
        return build_list

    def get_trading_routes(self):
        """
        :return: the village's trading routes.
        """
        self.newdid  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        trading_routes = 0
        return trading_routes

    def add_farm(self, farm):
        """
        adding a farm (RaidEntry) to the village's farm_list.
        """
        pass  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TODO

    def add_building(self):
        """
        adding a building to the village's building_list.
        """
        pass  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TODO

    def add_trading_route(self, trading_route):
        """
        adding a trading_route (TradingRouteEntry) to the village's trading_routes.
        """
        # 2
        pass  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TODO

    def __eq__(self, other):
        """
        :param other: (int)
        """
        return self.newdid == other


class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tribe = self.get_tribe()
        self.villages = {}  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        self.hero_location = self.get_hero_location()

    def get_tribe(self):
        """
        :return: the tribe's name. (string)
        """
        self.username  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO
        tribe = ""
        return tribe

    def get_hero_location(self):
        """
        :return: the hero's home village. (Village)
        """
        return self  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO

    def go_to_adventure(self):
        """
        checks if an adventure is available and if so - send hero to it, if he is available.
        """
        pass         # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO

    def relocate_hero_to(self, village):
        """
        changes the home village of the hero to the given village.
        """
        pass         # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TODO

    def __eq__(self, other):
        """
        :param other: (string)
        """
        return self.username == other


class Reinforcement:

    def __init__(self, source, target, troops, d):
        """
        :param source: (Village)
        :param target: (Village)
        :param troops: (t1, t2, ... , t10, t11). (tuple)
        :param d: the d code. (int)
        """
        self.source = source
        self.target = target
        self.troops = troops
        self.d = d

    def dispatch(self):
        """
        dispatches the reinforcement.
        """
        pass  # ~~~~~~~~~~~~~~~~~~~~~~~~~ TODO


class RaidEntry:

    def __init__(self, village, farm, troops):
        """
        :param village: (Village)
        :param farm: (Farm)
        :param troops: (t1, t2, t3, ... , t11). (tuple)
        """
        self.village = village
        self.farm = farm
        self.troops = troops


class TradingRouteEntry:

    def __init__(self, source, target, resources):
        """
        :param source: (Village)
        :param target: (Village)
        :param resources: (wood, clay, iron, crop). (tuple)
        """
        self.source = source
        self.target = target
        self.resources = resources


class BuildingTask:

    def __init__(self, village, gid, resources, id=None):
        """
        :param village: (Village)
        :param gid: the building's ID you'd like to upgrade. (string)
        :param resources: the resources needed to build this. (wood, clay, iron, crop). (tuple)
        :param id: (string)
        """
        self.village = village
        self.building_id = gid
        self.resources = resources
        self.id = id


class Farm:

    def __init__(self, name, x, y, z, residence=0, wall=0):
        """
        :param name: (string)
        :param x: (int)
        :param y: (int)
        :param z: (int)
        :param residence: (int)
        :param wall: (int)
        """
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.residence = residence
        self.wall = wall


class ReportsHandler:
    pass


class GUI:

    def __init__(self):

        def login(username=False, password=False):
            if username and password:
                bot = WebActions(username, password)
            else:
                global selected_username
                bot = WebActions(selected_username.get(), users_dic[selected_username.get()])
            global login_window
            login_window.destroy()
            self.bot_window(bot)
            del login_window, selected_username

        def added_and_login():
            if username_Entry.get() == "" or password_Entry.get() == "":
                messagebox.showerror("Error", "Please enter username and password")
            else:
                text = "Are you sure that you want to add '{}' as a new user with '{}' as it's password?".format(username_Entry.get(),
                                                                                                                 password_Entry.get())
                if messagebox.askyesno("Info Confirmation", text):
                    global users_option_menu
                    WebActions.add_user(username_Entry.get(), password_Entry.get())
                    login(username_Entry.get(), password_Entry.get())

        with open("users_dic.file", "rb") as rf:
            users_dic = dict(pickle.load(rf))

        usernames = []
        for username in users_dic.keys():
            usernames.append(username)

        global login_window
        login_window = tk.Tk()
        login_window.title("TravianBot Login")

        login_frame = tk.Frame(login_window, borderwidth=10)
        login_frame.pack()

        label1 = tk.Label(login_frame, text="Choose a User:")
        label1.pack()
        global selected_username
        selected_username = tk.StringVar(login_frame)
        selected_username.set("Please Select a User")
        users_option_menu = tk.OptionMenu(login_frame, selected_username, *usernames)
        users_option_menu.pack()
        login_button = tk.Button(login_frame, text="Login", command=login)
        login_button.pack()

        sep = ttk.Separator(login_window)
        sep.pack(fill="x")

        new_user_frame = tk.Frame(login_window, borderwidth=10)
        new_user_frame.pack()

        label2 = tk.Label(new_user_frame, text="Or enter a new one:")
        label2.grid(row=0, columnspan=2)
        username_label = tk.Label(new_user_frame, text="Username")
        password_label = tk.Label(new_user_frame, text="password")
        username_Entry = tk.Entry(new_user_frame)
        password_Entry = tk.Entry(new_user_frame)
        username_label.grid(row=1)
        password_label.grid(row=2)
        username_Entry.grid(row=1, column=1)
        password_Entry.grid(row=2, column=1)
        add_user_button = tk.Button(new_user_frame, text="Add and Login", command=added_and_login)
        add_user_button.grid(row=3, columnspan=2)

        login_window.mainloop()

    def bot_window(self, bot):

        browser = bot.browser

        def get_troops_from_box(browser, box_name):
            num = browser.find_element_by_name(box_name).get_attribute("value")
            try:
                return int(num)
            except:
                return 0

        #  Can't Raid with a hero.
        def add_raid():
            if browser.current_url.startswith('https://ts1.travian.co.il/build.php?id=39&tt=2&z='):
                a, z = browser.current_url.split("&z=")
                current_village = bot.get_current_village()
                raid = RaidEntry(current_village, z, (get_troops_from_box(browser, "t1"),
                                                      get_troops_from_box(browser, "t2"),
                                                      get_troops_from_box(browser, "t3"),
                                                      get_troops_from_box(browser, "t4"),
                                                      get_troops_from_box(browser, "t5"),
                                                      get_troops_from_box(browser, "t6"),
                                                      get_troops_from_box(browser, "t7"),
                                                      get_troops_from_box(browser, "t8"),
                                                      get_troops_from_box(browser, "t9"),
                                                      get_troops_from_box(browser, "t10"),
                                                      0))

                path = os.path.dirname(os.path.realpath(__file__))+"\\users\\{}\\{}".format(bot.user, current_village)+"\\raid_list.file"
                try:
                    with open(path, "rb") as rf:
                        raid_list = pickle.load(rf)
                except(EOFError):
                    raid_list = []

                raid_list.append(raid)

                with open(path, "wb") as wf:
                    pickle.dump(raid_list, wf)

                global add_raid_label
                add_raid_label.config(text='Raid successfully added!')
            else:
                messagebox.showerror("Error", 'Please click on a village and than "send troops"')

        def add_building_queue():
            pass

        root = tk.Tk()
        root.title("TravianBot")
        raid_frame = tk.Frame(root)
        raid_frame.pack()
        add_raid_button = tk.Button(raid_frame, text="Add Raid", command=add_raid)
        add_raid_button.pack()
        global add_raid_label
        add_raid_label = tk.Label(raid_frame)
        add_raid_label.pack()

        sep = ttk.Separator(root)
        sep.pack(fill="x")

        add_to_building_queue = tk.Frame(root)
        add_to_building_queue.pack()
        add_to_building_queue_button = tk.Button(add_to_building_queue, text="Add to building queue", command=add_building_queue)
        add_to_building_queue_button.pack()

        root.mainloop()


if __name__ == "__main__":
    # bot = WebActions("eliranisrael", "123saltfish")
    # print(bot.get_gid())

    gui = GUI()


