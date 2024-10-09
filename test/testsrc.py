import autotest_src
info="gnome-desktop gir1.2-gnomebg-4.0 42.9 0ubuntu1"
info=info.split(" ")
autotest_src.autotest_src(info[0],info[1],info[2],info[3],checkExist=False)
