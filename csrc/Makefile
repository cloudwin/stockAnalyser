cc = g++
prom = libbuyer.so
deps = $(shell find ./ -name "*.h")
src = $(shell find ./ -name "*.cpp")
obj = $(src:%.cpp=%.o) 
objfiles = $(shell find ./ -name "*.o")

CXXFLAGS += -I./ -I../
CXXFLAGS += -fopenmp

ifdef DEBUG
    CXXFLAGS += -g
else
	CXXFLAGS += -O2 -Wno-unused-result
endif

$(prom): register.g $(obj)
	$(cc) -o $(prom) $(obj) -shared -fPIC $(CXXFLAGS)

%.o: %.cpp $(deps)
	$(cc) -fPIC -c $< -o $@ $(CXXFLAGS)

clean:
	rm -rf $(objfiles) $(prom)
	rm ./register.g
	rm ./fileLoc.h
register.g: $(deps)
	./genRegister.py
#dbg: $(obj)
#	$(cc) -o $(prom) $(obj) -shared -fPIC -g

