PN         = btrdup
DOCS       = FAQ.md
MAN_MAN1   = pycheckit.1

ifeq ($(shell id -un), root)
  PREFIX    ?= /usr/local
else
  PREFIX    ?= $(HOME)/.local
endif
DOCDIR     = $(PREFIX)/share/doc/$(PN)
MAN1DIR    = $(PREFIX)/share/man/man1

ifeq ($(COMPRESS), yes)
  DOCS     := $(addsuffix .gz,$(DOCS))
  MAN_MAN1 := $(addsuffix .gz,$(MAN_MAN1))
  MAN_MAN5 := $(addsuffix .gz,$(MAN_MAN5))
endif

# convert using "asciidoctor": <https://asciidoctor.org>
ASCIIDOCTOR_MANPAGE = asciidoctor -d manpage -b manpage
ASCIIDOCTOR_HTML    = asciidoctor -b html5 -d article

# reproducible builds: reference date is ":date:" attribute from asciidoc source
date_attr = $(shell sed -rn 's/:date:\s*//p' $(1))
source_date_epoch = $(shell date +%s -u -d $(call date_attr,$(1)))


all: man
man: man1
man1: $(MAN_MAN1)

install: install-man 

install-man: man
	install -d -m 755 "$(DESTDIR)$(MAN1DIR)"
	install -p -m 644 $(MAN_MAN1) "$(DESTDIR)$(MAN1DIR)"
	install -p -m 644 $(MAN_MAN5) "$(DESTDIR)$(MAN1DIR)"

install-doc: $(DOCS)
	install -d -m 755 "$(DESTDIR)$(DOCDIR)"
	install -p -m 644 $(DOCS) "$(DESTDIR)$(DOCDIR)"

clean:
	rm -f *.md.gz *.[15] *.[15].{gz,html}

%.gz : %
	gzip -9 -n -c $< > $@

%.1 : %.1.asciidoc
	SOURCE_DATE_EPOCH=$(call source_date_epoch,$<) $(ASCIIDOCTOR_MANPAGE) -o $@ $<

%.5 : %.5.asciidoc
	SOURCE_DATE_EPOCH=$(call source_date_epoch,$<) $(ASCIIDOCTOR_MANPAGE) -o $@ $<

%.html : %.asciidoc
	SOURCE_DATE_EPOCH=$(call source_date_epoch,$<) $(ASCIIDOCTOR_HTML) -o $@ $<
