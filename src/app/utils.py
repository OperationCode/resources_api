class Paginator:
    def __init__(self, configuration, request):
        self.configuration = configuration

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    def items(self, query):
        return query.paginate(self.page, self.page_size, False).items
